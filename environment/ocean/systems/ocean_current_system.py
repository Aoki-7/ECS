#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
洋流系统 — 基于连续统框架的统一扩散

v4.0 重构：使用 continuum_utils 的通用扩散内核，
替代原有的独立距离扫描实现。

物理模型:
    暖流影响: dT/dt = C * (T_current - T_air) * exp(-r/R)
    寒流影响: dT/dt = C * (T_current - T_air) * exp(-r/R)
    盐度扩散: dS/dt = D * ∇²S

参数:
    C = 0.5 /h (温度影响系数)
    R = 30 m (影响半径)
    D = 0.01 /h (盐度扩散系数)

与其他模块的关系:
    - continuum/: 使用通用扩散内核 (compute_diffusion_flux)
    - environment/: 读取/写入 EnvironmentComponent (温度)
    - ocean/: 读取 OceanCurrentComponent (类型/温度/盐度)

版本: v4.0
"""

import logging
import math
from typing import Dict, Tuple, Optional

from core.sqrt_cache import cached_sqrt, cached_distance
from core.system import System
from core.world import World
from core.entity import Entity

from environment.ocean.components.ocean_current_component import OceanCurrentComponent
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

from environment.continuum.continuum_utils import (
    resolve_boundary,
    compute_diffusion_flux,
    clamp,
    get_neighbor_offsets,
)

logger = logging.getLogger(__name__)


class OceanCurrentSystem(System):
    """
    洋流系统

    使用连续统框架的通用扩散内核处理:
    1. 暖流/寒流影响周围温度 (指数衰减模型)
    2. 盐度平衡 (扩散模型)

    在管线中应运行在 EnvironmentalContinuumSystem 之后。
    """

    tick_interval = 10  # 每10帧执行一次

    # 温度影响参数
    TEMP_INFLUENCE_COEFF = 0.5    # 温度影响系数 (°C/h)
    TEMP_INFLUENCE_RANGE = 30    # 影响半径 (m)
    WARM_CURRENT_TEMP = 25.0     # 暖流温度 (°C)
    COLD_CURRENT_TEMP = 5.0      # 寒流温度 (°C)

    # 盐度扩散参数
    SALINITY_DIFFUSION_RATE = 0.01  # 盐度扩散系数 (1/h)
    MAX_SALINITY_CHANGE = 0.5      # 最大单步盐度变化

    def __init__(self, neighborhood: str = "moore"):
        super().__init__()
        self._neighbor_offsets = get_neighbor_offsets(neighborhood)

    def update(self, world: World, dt: float) -> None:
        """更新洋流"""
        grid = self._build_grid(world)
        if not grid:
            return

        bounds = self._compute_bounds(grid)

        # 洋流影响周围温度
        self._influence_temperature(world, grid, dt, bounds)

        # 盐度平衡
        self._balance_salinity(world, grid, dt, bounds)

    def _influence_temperature(self, world: World, grid: Dict, dt: float,
                               bounds: Optional[Tuple]) -> None:
        """洋流影响周围空气温度 — 使用指数衰减模型

        物理模型:
            暖流: ΔT = C * (T_warm - T_air) * exp(-r/R) * dt
            寒流: ΔT = C * (T_cold - T_air) * exp(-r/R) * dt
        """
        for key, eid in grid.items():
            current = world.get_component(eid, OceanCurrentComponent)
            if current is None:
                continue

            # 确定洋流温度
            if current.current_type == "warm":
                current_temp = self.WARM_CURRENT_TEMP
            elif current.current_type == "cold":
                current_temp = self.COLD_CURRENT_TEMP
            else:
                continue

            # 影响周围单元格 (包括有/没有 OceanCurrentComponent 的实体)
            for dx, dy in self._neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None:
                    continue

                # 查找邻居位置的环境实体 (可能不在 grid 中)
                neighbor_eid = grid.get(nk)
                if neighbor_eid is None:
                    continue

                n_env = world.get_component(neighbor_eid, EnvironmentComponent)
                if n_env is None:
                    continue

                # 计算距离
                dist = cached_distance(dx, dy)

                # 指数衰减影响
                influence = self.TEMP_INFLUENCE_COEFF * math.exp(-dist / self.TEMP_INFLUENCE_RANGE) * dt

                # 温度趋近洋流温度
                dT = current_temp - n_env.air_temperature
                n_env.air_temperature += influence * dT
                n_env.air_temperature = clamp(n_env.air_temperature, -30.0, 50.0)

    def _balance_salinity(self, world: World, grid: Dict, dt: float,
                        bounds: Optional[Tuple]) -> None:
        """盐度平衡 — 使用通用扩散内核

        物理模型:
            dS/dt = D * ∇²S
        """
        n_nei = len(self._neighbor_offsets)
        net_fluxes = {key: 0.0 for key in grid.keys()}

        for key, eid in grid.items():
            current = world.get_component(eid, OceanCurrentComponent)
            if current is None:
                continue

            for dx, dy in self._neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in grid:
                    continue

                n_current = world.get_component(grid[nk], OceanCurrentComponent)
                if n_current is None:
                    continue

                flux = compute_diffusion_flux(
                    current.salinity, n_current.salinity,
                    self.SALINITY_DIFFUSION_RATE, dt, self.MAX_SALINITY_CHANGE
                )

                net_fluxes[key] += flux
                net_fluxes[nk] -= flux

        # 应用净通量
        for key, net_flux in net_fluxes.items():
            current = world.get_component(grid[key], OceanCurrentComponent)
            if current is None:
                continue
            current.salinity += net_flux / n_nei
            current.salinity = clamp(current.salinity, 0.0, 50.0)

    def _build_grid(self, world: World) -> Dict[Tuple[int, int], Entity]:
        """构建网格索引 — 包含所有有 SpaceComponent 的实体"""
        grid = {}
        for entity, (space,) in world.get_components(SpaceComponent):
            if space is None:
                continue
            key = (int(space.x), int(space.y))
            grid[key] = entity
        return grid

    def _compute_bounds(self, grid: Dict) -> Optional[Tuple[int, int, int, int]]:
        """计算网格边界"""
        if not grid:
            return None
        xs = [k[0] for k in grid.keys()]
        ys = [k[1] for k in grid.keys()]
        return min(xs), max(xs), min(ys), max(ys)