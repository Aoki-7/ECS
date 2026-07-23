#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
侵蚀系统

v3.5 新增 — P0

职责：
    - 模拟风蚀、水蚀、冰川侵蚀
    - 改变地形海拔和坡度
    - 沉积物搬运和堆积

依赖：
    - StrataComponent
    - TerrainComponent
    - WaterBodyComponent（河流侵蚀）
"""

import logging
from typing import Dict, List, Optional

from core.system import System
from core.world import World

from environment.geology.components.strata_component import StrataComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.hydrology.components.water_body_component import WaterBodyComponent
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class ErosionSystem(System):
    """
    侵蚀系统

    每帧更新：
    1. 水蚀（降雨和河流）
    2. 风蚀（干旱地区）
    3. 沉积物搬运
    4. 地形变化
    """

    tick_interval = 20  # 每20帧执行一次（地质变化极慢）

    # 侵蚀参数
    WATER_EROSION_RATE = 0.001
    WIND_EROSION_RATE = 0.0001
    SEDIMENT_TRANSPORT_RATE = 0.01

    def update(self, world: World, dt: float) -> None:
        """更新侵蚀"""
        # 水蚀
        self._process_water_erosion(world, dt)

        # 风蚀
        self._process_wind_erosion(world, dt)

        # 沉积物搬运
        self._process_sediment_transport(world, dt)

    def _process_water_erosion(self, world: World, dt: float) -> None:
        """水蚀：降雨和河流冲刷地形"""
        for entity, (terrain, strata, space) in world.get_components(
            TerrainComponent, StrataComponent, SpaceComponent
        ):
            if terrain is None or strata is None:
                continue

            # 查找附近水体
            nearby_water = self._find_nearby_water(world, space)

            if nearby_water:
                # 河流侵蚀
                erosion = nearby_water.flow_rate * self.WATER_EROSION_RATE * dt
                terrain.elevation = max(0.0, terrain.elevation - erosion)

                # 增加沉积物
                if not hasattr(terrain, 'sediment'):
                    terrain.sediment = 0.0
                terrain.sediment += erosion

    def _process_wind_erosion(self, world: World, dt: float) -> None:
        """风蚀：干旱地区地形变化"""
        for entity, (terrain, space) in world.get_components(
            TerrainComponent, SpaceComponent
        ):
            if terrain is None:
                continue

            # 只有干旱地区有风蚀
            env = world.get_component(entity, EnvironmentComponent)
            if env is None or env.air_humidity > 0.3:
                continue

            # 风速越大侵蚀越强
            wind_erosion = env.wind_speed * self.WIND_EROSION_RATE * dt
            terrain.elevation = max(0.0, terrain.elevation - wind_erosion)

    def _process_sediment_transport(self, world: World, dt: float) -> None:
        """沉积物搬运：从高处搬运到低处"""
        # 收集所有带地形和沉积物的实体
        entities_with_sediment = []
        for entity, (terrain, space) in world.get_components(
            TerrainComponent, SpaceComponent
        ):
            if terrain is None or not hasattr(terrain, 'sediment'):
                continue
            if terrain.sediment > 0:
                entities_with_sediment.append((entity, terrain, space))

        # 搬运沉积物到更低的位置
        for entity, terrain, space in entities_with_sediment:
            # 寻找附近更低的点
            lower_target = self._find_lower_neighbor(world, space, terrain.elevation)

            if lower_target:
                target_entity, target_terrain = lower_target
                transport_amount = terrain.sediment * self.SEDIMENT_TRANSPORT_RATE * dt

                terrain.sediment -= transport_amount
                if not hasattr(target_terrain, 'sediment'):
                    target_terrain.sediment = 0.0
                target_terrain.sediment += transport_amount

                # 低处堆积增加海拔
                target_terrain.elevation += transport_amount * 0.5

    def _find_nearby_water(self, world: World, space: SpaceComponent) -> Optional[WaterBodyComponent]:
        """查找附近的水体"""
        nearest = None
        nearest_dist = float('inf')

        for entity, (water, wb_space) in world.get_components(WaterBodyComponent, SpaceComponent):
            if water is None or wb_space is None:
                continue
            dist = ((space.x - wb_space.x) ** 2 + (space.y - wb_space.y) ** 2) ** 0.5
            if dist < nearest_dist and dist < 20:
                nearest_dist = dist
                nearest = water

        return nearest

    def _find_lower_neighbor(self, world: World, space: SpaceComponent, elevation: float):
        """寻找附近海拔更低的邻居"""
        best = None
        best_elevation = elevation

        for entity, (terrain, other_space) in world.get_components(
            TerrainComponent, SpaceComponent
        ):
            if terrain is None or other_space is None:
                continue
            dist = ((space.x - other_space.x) ** 2 + (space.y - other_space.y) ** 2) ** 0.5
            if dist < 10 and terrain.elevation < best_elevation:
                best_elevation = terrain.elevation
                best = (entity, terrain)

        return best