#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
污染扩散系统 — 基于连续统框架的统一扩散

v4.0 重构：使用 continuum_utils 的通用扩散内核，
替代原有的独立扩散实现。

物理模型:
    空气扩散: dC_air/dt = D_air * ∇²C_air * wind_factor - decay
    水扩散:   dC_water/dt = D_water * ∇²C_water - decay
    土壤扩散: dC_soil/dt = D_soil * ∇²C_soil - decay

参数:
    D_air = 0.05 /h (空气扩散系数)
    D_water = 0.03 /h (水扩散系数)
    D_soil = 0.01 /h (土壤扩散系数)
    decay = 0.001 /h (自然降解速率)

与其他模块的关系:
    - continuum/: 使用通用扩散内核 (compute_diffusion_flux)
    - environment/: 读取风速 (wind_speed) 影响空气扩散
    - pollution/: 读取/写入 PollutionComponent

版本: v4.0
"""

import logging
from typing import Dict, Tuple, Optional

from core.system import System
from core.world import World
from core.entity import Entity

from environment.pollution.components.pollution_component import PollutionComponent
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

from environment.continuum.continuum_utils import (
    ContinuumCache,
    resolve_boundary,
    compute_diffusion_flux,
    clamp,
    get_neighbor_offsets,
)

logger = logging.getLogger(__name__)


class PollutionDiffusionSystem(System):
    """
    污染扩散系统

    使用连续统框架的通用扩散内核，统一处理空气/水/土壤污染扩散。

    在管线中应运行在 EnvironmentalContinuumSystem 之后，
    利用连续统建立的环境梯度进行污染扩散。
    """

    tick_interval = 5  # 每5帧执行一次

    # 扩散参数
    AIR_DIFFUSION_RATE = 0.05    # 空气扩散系数 (1/h)
    WATER_DIFFUSION_RATE = 0.03  # 水扩散系数 (1/h)
    SOIL_DIFFUSION_RATE = 0.01   # 土壤扩散系数 (1/h)
    NATURAL_DECAY = 0.001        # 自然降解速率 (1/h)
    MAX_CHANGE = 0.1             # 最大单步变化

    def __init__(self, neighborhood: str = "moore"):
        super().__init__()
        self._neighbor_offsets = get_neighbor_offsets(neighborhood)

    def update(self, world: World, dt: float) -> None:
        """更新污染扩散"""
        grid = self._build_grid(world)
        if not grid:
            return

        bounds = self._compute_bounds(grid)
        cache = self._build_cache(world, grid)

        # 空气扩散 (随风速增强)
        self._diffuse_air(world, cache, grid, dt, bounds)

        # 水扩散
        self._diffuse_water(world, cache, grid, dt, bounds)

        # 土壤扩散
        self._diffuse_soil(world, cache, grid, dt, bounds)

        # 自然降解
        self._natural_decay(world, cache, dt)

    def _diffuse_air(self, world: World, cache: Dict, grid: Dict, dt: float,
                     bounds: Optional[Tuple]) -> None:
        """空气污染物扩散 — 使用通用扩散内核
        
        优化：先缓存所有污染值，避免循环内重复get_component
        """
        n_nei = len(self._neighbor_offsets)
        
        # 缓存污染值和环境数据，避免循环内重复查询
        pollution_cache = {}
        env_cache = {}
        for key, eid in grid.items():
            pollution = world.get_component(eid, PollutionComponent)
            env = world.get_component(eid, EnvironmentComponent)
            if pollution is not None:
                pollution_cache[key] = pollution.air_pollution
                env_cache[key] = env.wind_speed if env else 1.0

        # 计算每个单元格的净通量
        net_fluxes = {key: 0.0 for key in pollution_cache.keys()}
        
        for key in pollution_cache:
            c_self = pollution_cache[key]
            wind_factor = env_cache[key]
            eff_diff = self.AIR_DIFFUSION_RATE * wind_factor

            for dx, dy in self._neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in pollution_cache:
                    continue

                c_neighbor = pollution_cache[nk]
                flux = compute_diffusion_flux(c_self, c_neighbor, eff_diff, dt, self.MAX_CHANGE)
                net_fluxes[key] += flux
                net_fluxes[nk] -= flux

        # 应用净通量
        for key, net_flux in net_fluxes.items():
            eid = grid[key]
            pollution = world.get_component(eid, PollutionComponent)
            if pollution is None:
                continue
            pollution.air_pollution += net_flux
            pollution.air_pollution = clamp(pollution.air_pollution, 0.0, 1.0)

    def _diffuse_water(self, world: World, cache: Dict, grid: Dict, dt: float,
                       bounds: Optional[Tuple]) -> None:
        """水污染物扩散 — 优化版：先缓存污染值"""
        n_nei = len(self._neighbor_offsets)
        
        # 缓存污染值
        pollution_cache = {}
        for key, eid in grid.items():
            pollution = world.get_component(eid, PollutionComponent)
            if pollution is not None:
                pollution_cache[key] = pollution.water_pollution

        # 计算净通量
        net_fluxes = {key: 0.0 for key in pollution_cache.keys()}
        
        for key in pollution_cache:
            c_self = pollution_cache[key]
            for dx, dy in self._neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in pollution_cache:
                    continue

                c_neighbor = pollution_cache[nk]
                flux = compute_diffusion_flux(c_self, c_neighbor, self.WATER_DIFFUSION_RATE, dt, self.MAX_CHANGE)
                net_fluxes[key] += flux
                net_fluxes[nk] -= flux

        # 应用净通量
        for key, net_flux in net_fluxes.items():
            eid = grid[key]
            pollution = world.get_component(eid, PollutionComponent)
            if pollution is None:
                continue
            pollution.water_pollution += net_flux / n_nei
            pollution.water_pollution = clamp(pollution.water_pollution, 0.0, 1.0)

    def _diffuse_soil(self, world: World, cache: Dict, grid: Dict, dt: float,
                      bounds: Optional[Tuple]) -> None:
        """土壤污染物扩散 — 优化版：先缓存污染值"""
        n_nei = len(self._neighbor_offsets)
        
        # 缓存污染值
        pollution_cache = {}
        for key, eid in grid.items():
            pollution = world.get_component(eid, PollutionComponent)
            if pollution is not None and pollution.soil_pollution > 0:
                pollution_cache[key] = pollution.soil_pollution

        # 计算净通量
        net_fluxes = {key: 0.0 for key in pollution_cache.keys()}
        
        for key in pollution_cache:
            c_self = pollution_cache[key]
            for dx, dy in self._neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in pollution_cache:
                    continue

                c_neighbor = pollution_cache[nk]
                flux = compute_diffusion_flux(c_self, c_neighbor, self.SOIL_DIFFUSION_RATE, dt, self.MAX_CHANGE)
                net_fluxes[key] += flux
                net_fluxes[nk] -= flux

        # 应用净通量
        for key, net_flux in net_fluxes.items():
            eid = grid[key]
            pollution = world.get_component(eid, PollutionComponent)
            if pollution is None:
                continue
            pollution.soil_pollution += net_flux / n_nei
            pollution.soil_pollution = clamp(pollution.soil_pollution, 0.0, 1.0)

    def _natural_decay(self, world: World, cache: Dict, dt: float) -> None:
        """污染自然降解 — 优化版：批量处理"""
        decay = self.NATURAL_DECAY * dt
        
        for key, eid in cache.items():
            pollution = world.get_component(eid, PollutionComponent)
            if pollution is None:
                continue

            pollution.air_pollution = max(0.0, pollution.air_pollution - decay)
            pollution.water_pollution = max(0.0, pollution.water_pollution - decay)
            pollution.soil_pollution = max(0.0, pollution.soil_pollution - decay)

            # 污染物浓度降解
            to_remove = []
            for pollutant_type, value in pollution.pollutants.items():
                new_value = max(0.0, value - decay * 10)
                if new_value <= 0:
                    to_remove.append(pollutant_type)
                else:
                    pollution.pollutants[pollutant_type] = new_value
            
            for pollutant_type in to_remove:
                del pollution.pollutants[pollutant_type]

    def _build_grid(self, world: World) -> Dict[Tuple[int, int], Entity]:
        """构建网格索引"""
        grid = {}
        for entity, (space, pollution) in world.get_components(SpaceComponent, PollutionComponent):
            if space is None or pollution is None:
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

    def _build_cache(self, world: World, grid: Dict) -> Dict:
        """构建缓存"""
        cache = {}
        for key, eid in grid.items():
            cache[key] = eid
        return cache