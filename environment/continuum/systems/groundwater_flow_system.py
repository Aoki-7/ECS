#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地下水流动系统 — 水头梯度驱动的地下水流

v4.0 新增 — Phase 2

物理模型:
    1. 水头计算: 水头 = 海拔 + 水表深度
    2. 达西定律: 流速 = 渗透系数 * 水头梯度
    3. 渗透系数: 土壤质地决定 (砂土 > 壤土 > 粘土)
    4. 补给: 降雨/河流 → 地下水
    5. 排泄: 地下水 → 河流/泉水/蒸发

参数:
    HYDRAULIC_CONDUCTIVITY_SAND = 10.0 m/h (砂土渗透系数)
    HYDRAULIC_CONDUCTIVITY_LOAM = 1.0 m/h (壤土渗透系数)
    HYDRAULIC_CONDUCTIVITY_CLAY = 0.01 m/h (粘土渗透系数)
    RECHARGE_RATE = 0.1 /h (补给速率)
    DISCHARGE_RATE = 0.05 /h (排泄速率)

与其他模块的关系:
    - continuum/: 使用通用扩散内核 (compute_diffusion_flux)
    - hydrology/: 读取/写入 GroundwaterComponent
    - soil/: 读取土壤质地 (渗透系数)
    - terrain/: 读取海拔 (水头计算)

版本: v4.0
"""

import logging
import math
from typing import Dict, Tuple, Optional

from core.sqrt_cache import cached_sqrt, cached_distance
from core.system import System
from core.world import World
from core.entity import Entity

from environment.hydrology.components.groundwater_component import GroundwaterComponent
from environment.soil.components.soil_component import SoilComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

from environment.continuum.continuum_utils import (
    resolve_boundary,
    compute_diffusion_flux,
    clamp,
    get_neighbor_offsets,
)

logger = logging.getLogger(__name__)


class GroundwaterFlowSystem(System):
    """
    地下水流动系统

    使用连续统框架:
    1. 计算水头 (海拔 + 水表深度)
    2. 使用通用扩散内核模拟达西流动
    3. 补给/排泄作为源/汇

    在管线中应运行在 WaterCycleSystem 之后。
    """

    tick_interval = 10  # 每10帧执行一次

    # 渗透系数 (m/h)
    K_SAND = 10.0
    K_LOAM = 1.0
    K_CLAY = 0.01

    # 补给/排泄速率
    RECHARGE_RATE = 0.1
    DISCHARGE_RATE = 0.05

    def __init__(self, neighborhood: str = "moore"):
        super().__init__()
        self._neighbor_offsets = get_neighbor_offsets(neighborhood)

    def update(self, world: World, dt: float) -> None:
        """更新地下水流动"""
        grid = self._build_grid(world)
        if not grid:
            return

        bounds = self._compute_bounds(grid)

        # 1. 计算水头
        heads = self._compute_heads(world, grid)

        # 2. 地下水流动 (达西定律)
        self._process_groundwater_flow(world, grid, heads, dt, bounds)

        # 3. 补给 (降雨/河流)
        self._process_recharge(world, grid, dt)

        # 4. 排泄 (河流/泉水/蒸发)
        self._process_discharge(world, grid, dt)

    def _compute_heads(self, world: World, grid: Dict) -> Dict[Tuple[int, int], float]:
        """计算水头 (海拔 + 水表深度)"""
        heads = {}
        for key, eid in grid.items():
            terrain = world.get_component(eid, TerrainComponent)
            groundwater = world.get_component(eid, GroundwaterComponent)

            elevation = terrain.elevation if terrain else 0.0
            water_table = groundwater.water_table if groundwater else -5.0

            # 水头 = 海拔 + 水表深度 (负值表示地下)
            heads[key] = elevation + water_table

        return heads

    def _process_groundwater_flow(self, world: World, grid: Dict, heads: Dict,
                                  dt: float, bounds: Optional[Tuple]) -> None:
        """地下水流动 — 达西定律 — 优化版：先缓存渗透系数"""
        n_nei = len(self._neighbor_offsets)
        
        # 缓存渗透系数和地下水组件，避免循环内重复get_component
        k_cache = {}
        groundwater_cache = {}
        for key, eid in grid.items():
            groundwater = world.get_component(eid, GroundwaterComponent)
            soil = world.get_component(eid, SoilComponent)
            if groundwater is not None:
                k_cache[key] = self._get_hydraulic_conductivity(soil)
                groundwater_cache[key] = groundwater

        # 计算净通量
        net_fluxes = {key: 0.0 for key in groundwater_cache.keys()}
        
        for key in groundwater_cache:
            k = k_cache[key]
            
            for dx, dy in self._neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in groundwater_cache:
                    continue

                # 达西定律: 流速 = K * (H1 - H2) / L
                head_diff = heads[key] - heads[nk]
                dist = cached_distance(dx, dy)

                # 有效扩散系数
                n_k = k_cache[nk]
                avg_k = (k + n_k) / 2.0
                eff_diff = avg_k / max(dist, 0.1)

                flux = compute_diffusion_flux(
                    heads[key], heads[nk],
                    eff_diff, dt, 1.0
                )

                net_fluxes[key] += flux
                net_fluxes[nk] -= flux

        # 应用净通量
        for key, net_flux in net_fluxes.items():
            groundwater = groundwater_cache[key]
            groundwater.water_table += net_flux / n_nei

    def _get_hydraulic_conductivity(self, soil: Optional[SoilComponent]) -> float:
        """获取渗透系数"""
        if soil is None:
            return self.K_LOAM

        # 基于土壤质地
        if hasattr(soil, 'soil_type') and soil.soil_type == "sand":
            return self.K_SAND
        elif hasattr(soil, 'soil_type') and soil.soil_type == "clay":
            return self.K_CLAY
        else:
            return self.K_LOAM

    def _process_recharge(self, world: World, grid: Dict, dt: float) -> None:
        """补给: 降雨/河流 → 地下水"""
        for key, eid in grid.items():
            groundwater = world.get_component(eid, GroundwaterComponent)
            env = world.get_component(eid, EnvironmentComponent)
            if groundwater is None or env is None:
                continue

            # 降雨补给
            if env.rainfall > 0:
                recharge = env.rainfall * self.RECHARGE_RATE * dt * 0.1
                groundwater.water_table += recharge

            # 河流补给 (如果附近有河流)
            # TODO: 检查邻居是否有河流

    def _process_discharge(self, world: World, grid: Dict, dt: float) -> None:
        """排泄: 地下水 → 河流/泉水/蒸发"""
        for key, eid in grid.items():
            groundwater = world.get_component(eid, GroundwaterComponent)
            env = world.get_component(eid, EnvironmentComponent)
            if groundwater is None or env is None:
                continue

            # 蒸发排泄 (浅层地下水)
            if groundwater.water_table > -1.0:  # 接近地表
                discharge = self.DISCHARGE_RATE * dt
                groundwater.water_table -= discharge

            # 泉水排泄 (水头高于地表)
            terrain = world.get_component(eid, TerrainComponent)
            if terrain is not None:
                head = terrain.elevation + groundwater.water_table
                if head > terrain.elevation:
                    # 泉水流出
                    spring_discharge = (head - terrain.elevation) * self.DISCHARGE_RATE * dt
                    groundwater.water_table -= spring_discharge

    def _build_grid(self, world: World) -> Dict[Tuple[int, int], Entity]:
        """构建网格索引"""
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
