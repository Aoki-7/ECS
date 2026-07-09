#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CO₂/O₂ 扩散系统 — 气体浓度梯度交换

v4.0 新增 — Phase 2

物理模型:
    1. CO₂ 扩散: 植物光合消耗 → 浓度降低 → 从周围补充
    2. O₂ 扩散: 植物光合产生 → 浓度升高 → 向周围扩散
    3. 呼吸作用: 生物呼吸消耗 O₂ 产生 CO₂
    4. 大气交换: 与上层大气缓慢交换

参数:
    CO2_DIFFUSION_RATE = 0.02 /h (CO₂ 扩散系数)
    O2_DIFFUSION_RATE = 0.02 /h (O₂ 扩散系数)
    RESPIRATION_RATE = 0.001 /h (呼吸速率)
    ATMOSPHERIC_CO2 = 420 ppm (大气 CO₂ 基准)
    ATMOSPHERIC_O2 = 21% (大气 O₂ 基准)

与其他模块的关系:
    - continuum/: 使用通用扩散内核 (compute_diffusion_flux)
    - plant/: 读取光合作用速率 (CO₂ 消耗/O₂ 产生)
    - animal/human/: 读取呼吸速率 (O₂ 消耗/CO₂ 产生)
    - environment/: 读取/写入 CO₂/O₂ 浓度

版本: v4.0
"""

import logging
from typing import Dict, Tuple, Optional

from core.system import System
from core.world import World
from core.entity import Entity

from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

from environment.continuum.continuum_utils import (
    resolve_boundary,
    compute_diffusion_flux,
    clamp,
    get_neighbor_offsets,
)

logger = logging.getLogger(__name__)


class GasDiffusionSystem(System):
    """
    CO₂/O₂ 扩散系统

    使用连续统框架:
    1. 通用扩散内核处理 CO₂/O₂ 浓度梯度
    2. 生物活动 (光合/呼吸) 作为源/汇
    3. 大气交换作为边界条件

    在管线中应运行在 EnvironmentalContinuumSystem 之后。
    """

    tick_interval = 10  # 每10帧执行一次

    # 气体扩散参数
    CO2_DIFFUSION_RATE = 0.02   # CO₂ 扩散系数 (1/h)
    O2_DIFFUSION_RATE = 0.02    # O₂ 扩散系数 (1/h)
    RESPIRATION_RATE = 0.001    # 呼吸速率 (1/h)

    # 大气基准值
    ATMOSPHERIC_CO2 = 420.0     # 大气 CO₂ (ppm)
    ATMOSPHERIC_O2 = 21.0       # 大气 O₂ (%)

    def __init__(self, neighborhood: str = "moore"):
        super().__init__()
        self._neighbor_offsets = get_neighbor_offsets(neighborhood)

        # 网格与组件缓存：环境单元是静态的，首次构建后复用
        self._grid_cache: Optional[Dict] = None
        self._bounds_cache: Optional[Tuple] = None
        self._env_cache: Optional[Dict] = None

    def update(self, world: World, dt: float) -> None:
        """更新气体扩散"""
        if self._grid_cache is None:
            grid = self._build_grid(world)
            if not grid:
                return
            self._grid_cache = grid
            self._bounds_cache = self._compute_bounds(grid)
            self._env_cache = {
                k: world.get_component(eid, EnvironmentComponent)
                for k, eid in grid.items()
            }

        grid = self._grid_cache
        bounds = self._bounds_cache
        env_cache = self._env_cache

        # 1. CO₂ 扩散
        self._diffuse_co2(grid, env_cache, dt, bounds)

        # 2. O₂ 扩散
        self._diffuse_o2(grid, env_cache, dt, bounds)

        # 3. 呼吸作用 (简化: 所有生物平均呼吸)
        self._process_respiration(grid, env_cache, dt)

        # 4. 大气交换 (边界条件)
        self._atmospheric_exchange(grid, env_cache, dt)

    def _diffuse_co2(self, grid: Dict, env_cache: Dict, dt: float,
                     bounds: Optional[Tuple]) -> None:
        """CO₂ 扩散 — 使用已缓存的环境组件"""
        n_nei = len(self._neighbor_offsets)

        # 缓存 CO₂ 浓度快照
        co2_cache = {key: env.co2 for key, env in env_cache.items() if env is not None}
        net_fluxes = {key: 0.0 for key in co2_cache.keys()}

        for key in co2_cache:
            c_self = co2_cache[key]
            for dx, dy in self._neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in co2_cache:
                    continue

                c_neighbor = co2_cache[nk]
                flux = compute_diffusion_flux(c_self, c_neighbor, self.CO2_DIFFUSION_RATE, dt, 50.0)
                net_fluxes[key] += flux
                net_fluxes[nk] -= flux

        # 应用净通量
        for key, net_flux in net_fluxes.items():
            env = env_cache[key]
            env.co2 = clamp(env.co2 + net_flux / n_nei, 200.0, 1000.0)

    def _diffuse_o2(self, grid: Dict, env_cache: Dict, dt: float,
                    bounds: Optional[Tuple]) -> None:
        """O₂ 扩散 — 使用已缓存的环境组件"""
        n_nei = len(self._neighbor_offsets)

        o2_cache = {key: env.o2 for key, env in env_cache.items() if env is not None}
        net_fluxes = {key: 0.0 for key in o2_cache.keys()}

        for key in o2_cache:
            c_self = o2_cache[key]
            for dx, dy in self._neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in o2_cache:
                    continue

                c_neighbor = o2_cache[nk]
                flux = compute_diffusion_flux(c_self, c_neighbor, self.O2_DIFFUSION_RATE, dt, 1.0)
                net_fluxes[key] += flux
                net_fluxes[nk] -= flux

        # 应用净通量
        for key, net_flux in net_fluxes.items():
            env = env_cache[key]
            env.o2 = clamp(env.o2 + net_flux / n_nei, 15.0, 25.0)
            env.o2 = clamp(env.o2, 15.0, 30.0)

    def _process_respiration(self, grid: Dict, env_cache: Dict, dt: float) -> None:
        """呼吸作用 — 简化模型"""
        for env in env_cache.values():
            if env is None:
                continue

            # 呼吸消耗 O₂ 产生 CO₂
            respiration = self.RESPIRATION_RATE * dt

            env.o2 = max(15.0, env.o2 - respiration)
            env.co2 = min(1000.0, env.co2 + respiration * 20)  # CO₂ 增量更大

    def _atmospheric_exchange(self, grid: Dict, env_cache: Dict, dt: float) -> None:
        """大气交换 — 边界条件"""
        for env in env_cache.values():
            if env is None:
                continue

            # 缓慢向大气基准值回归
            co2_diff = self.ATMOSPHERIC_CO2 - env.co2
            o2_diff = self.ATMOSPHERIC_O2 - env.o2

            env.co2 += co2_diff * 0.001 * dt
            env.o2 += o2_diff * 0.001 * dt

    def _build_grid(self, world: World) -> Dict[Tuple[int, int], Entity]:
        """构建网格索引：只包含完整环境单元"""
        grid = {}
        for entity, (space, _env) in world.get_components(
            SpaceComponent, EnvironmentComponent
        ):
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
