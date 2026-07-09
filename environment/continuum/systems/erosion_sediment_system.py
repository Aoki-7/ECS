#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
土壤侵蚀/沉积系统 — 水流携带土壤颗粒

v4.0 新增 — Phase 2

物理模型:
    1. 侵蚀: 水流速度 > 阈值 → 携带土壤颗粒
    2. 沉积: 水流速度 < 阈值 → 沉积土壤颗粒
    3. 搬运: 使用连续统重力水流模型 (已存在)
    4. 沉积分布: 坡度减缓处沉积更多

参数:
    EROSION_THRESHOLD = 0.5 m/s (侵蚀流速阈值)
    SEDIMENT_CAPACITY = 0.1 kg/m³ (最大含沙量)
    DEPOSITION_RATE = 0.01 /h (沉积速率)

与其他模块的关系:
    - continuum/: 使用重力水流模型 (GravityWaterFlowProcessor)
    - environment/: 读取水流速度/降雨
    - soil/: 读取/写入土壤属性 (厚度/质地)
    - terrain/: 读取海拔/坡度

版本: v4.0
"""

import logging
import math
from typing import Dict, Tuple, Optional

from core.sqrt_cache import cached_sqrt, cached_distance
from core.system import System
from core.world import World
from core.entity import Entity

from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from environment.terrain.components.terrain_component import TerrainComponent
from space.space_component import SpaceComponent

from environment.continuum.continuum_utils import (
    resolve_boundary,
    clamp,
    get_neighbor_offsets,
)
from environment.continuum.continuum_config import (
    WATER_FLOW_BASE_RATE,
    WATER_FLOW_SLOPE_EXPONENT,
)

logger = logging.getLogger(__name__)


class ErosionSedimentSystem(System):
    """
    土壤侵蚀/沉积系统

    使用连续统框架:
    1. 重力水流模型计算流速 (已有 GravityWaterFlowProcessor)
    2. 本系统根据流速计算侵蚀/沉积

    在管线中应运行在 GravityWaterFlowProcessor 之后。
    """

    tick_interval = 10  # 每10帧执行一次

    # 侵蚀参数
    EROSION_THRESHOLD = 0.5    # 侵蚀流速阈值 (m/s)
    SEDIMENT_CAPACITY = 0.1    # 最大含沙量 (kg/m³)
    DEPOSITION_RATE = 0.01     # 沉积速率 (1/h)
    EROSION_RATE = 0.02        # 侵蚀速率 (1/h)

    def __init__(self, neighborhood: str = "moore"):
        super().__init__()
        self._neighbor_offsets = get_neighbor_offsets(neighborhood)

    def update(self, world: World, dt: float) -> None:
        """更新侵蚀/沉积"""
        grid = self._build_grid(world)
        if not grid:
            return

        bounds = self._compute_bounds(grid)

        # 1. 计算侵蚀
        self._process_erosion(world, grid, dt, bounds)

        # 2. 计算沉积
        self._process_deposition(world, grid, dt, bounds)

    def _process_erosion(self, world: World, grid: Dict, dt: float,
                         bounds: Optional[Tuple]) -> None:
        """侵蚀: 高速水流携带土壤"""
        # 预取海拔
        elevs = {}
        for key, eid in grid.items():
            terrain = world.get_component(eid, TerrainComponent)
            elevs[key] = terrain.elevation if terrain else 0.0

        for key, eid in grid.items():
            soil = world.get_component(eid, SoilComponent)
            env = world.get_component(eid, EnvironmentComponent)
            if soil is None or env is None:
                continue

            # 计算流速 (简化模型)
            flow_velocity = self._compute_flow_velocity(key, grid, elevs, bounds)

            # 流速超过阈值 → 侵蚀
            if flow_velocity > self.EROSION_THRESHOLD:
                erosion_amount = (flow_velocity - self.EROSION_THRESHOLD) * self.EROSION_RATE * dt
                erosion_amount = min(erosion_amount, soil.thickness * 0.1)

                soil.thickness = max(0.0, soil.thickness - erosion_amount)
                soil.sediment_load = min(self.SEDIMENT_CAPACITY, soil.sediment_load + erosion_amount)

                logger.debug(f"Erosion at {key}: velocity={flow_velocity:.2f}, amount={erosion_amount:.4f}")

    def _process_deposition(self, world: World, grid: Dict, dt: float,
                            bounds: Optional[Tuple]) -> None:
        """沉积: 低速水流/坡度减缓处沉积"""
        # 预取海拔
        elevs = {}
        for key, eid in grid.items():
            terrain = world.get_component(eid, TerrainComponent)
            elevs[key] = terrain.elevation if terrain else 0.0

        for key, eid in grid.items():
            soil = world.get_component(eid, SoilComponent)
            env = world.get_component(eid, EnvironmentComponent)
            if soil is None or env is None:
                continue

            # 有沉积物
            if soil.sediment_load <= 0:
                continue

            # 计算流速
            flow_velocity = self._compute_flow_velocity(key, grid, elevs, bounds)

            # 流速低 → 沉积
            if flow_velocity < self.EROSION_THRESHOLD * 0.5:
                deposition_amount = soil.sediment_load * self.DEPOSITION_RATE * dt
                deposition_amount = min(deposition_amount, soil.sediment_load)

                soil.sediment_load -= deposition_amount
                soil.thickness += deposition_amount

                logger.debug(f"Deposition at {key}: amount={deposition_amount:.4f}")

    def _compute_flow_velocity(self, key: Tuple[int, int], grid: Dict, elevs: Dict,
                               bounds: Optional[Tuple]) -> float:
        """计算流速 (简化模型)"""
        max_velocity = 0.0

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
            if nk is None or nk not in grid:
                continue

            # 计算坡度
            elev_diff = elevs[key] - elevs.get(nk, 0.0)

            if elev_diff <= 0:
                continue

            dist = cached_distance(dx, dy)
            slope = elev_diff / max(dist, 0.1)

            velocity = WATER_FLOW_BASE_RATE * (slope ** WATER_FLOW_SLOPE_EXPONENT)
            max_velocity = max(max_velocity, velocity)

        return max_velocity

    def _build_grid(self, world: World) -> Dict[Tuple[int, int], Entity]:
        """构建网格索引：只包含完整环境单元（土壤+地形+环境）"""
        grid = {}
        for entity, (space, _soil, _terrain, _env) in world.get_components(
            SpaceComponent, SoilComponent, TerrainComponent, EnvironmentComponent
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
