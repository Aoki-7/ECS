#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水循环系统

v3.5 新增 — P0

职责：
    - 模拟水循环：蒸发 → 降水 → 径流 → 渗透 → 地下水
    - 管理水体之间的水流
    - 与土壤湿度、环境天气交互

依赖：
    - WaterBodyComponent
    - GroundwaterComponent
    - EnvironmentComponent（降雨、蒸发）
    - SoilComponent（土壤湿度）
"""

import logging
from typing import Dict, List, Optional

from core.system import System
from core.world import World

from environment.hydrology.components.water_body_component import WaterBodyComponent
from environment.hydrology.components.groundwater_component import GroundwaterComponent
from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class WaterCycleSystem(System):
    """
    水循环系统

    每帧更新：
    1. 降雨补充水体和土壤
    2. 蒸发减少水体
    3. 径流（土壤饱和后流向水体）
    4. 渗透（土壤向地下水补给）
    5. 地下水向水体排泄
    6. 河流流动（上游向下游）
    """

    tick_interval = 5  # 每5帧执行一次（水循环较慢）

    # 水循环参数
    EVAPORATION_RATE = 0.001  # 基础蒸发速率
    INFILTRATION_RATE = 0.01  # 渗透速率
    RUNOFF_THRESHOLD = 0.9    # 土壤饱和度超过此值产生径流
    GROUNDWATER_DISCHARGE = 0.005  # 地下水排泄速率

    def update(self, world: World, dt: float) -> None:
        """更新水循环"""
        # 1. 处理降雨
        self._process_rainfall(world, dt)

        # 2. 处理蒸发
        self._process_evaporation(world, dt)

        # 3. 处理渗透和径流
        self._process_infiltration_and_runoff(world, dt)

        # 4. 处理地下水交换
        self._process_groundwater_exchange(world, dt)

        # 5. 处理河流流动
        self._process_river_flow(world, dt)

    def _process_rainfall(self, world: World, dt: float) -> None:
        """降雨补充水体和土壤"""
        for entity, (env, soil, space) in world.get_components(
            EnvironmentComponent, SoilComponent, SpaceComponent
        ):
            if env is None or soil is None:
                continue

            rainfall = env.rainfall * dt
            if rainfall <= 0:
                continue

            # 70% 降雨进入土壤
            soil_infiltration = rainfall * 0.7
            soil.moisture = min(1.0, soil.moisture + soil_infiltration * 0.01)

            # 30% 形成地表水（寻找附近水体）
            surface_water = rainfall * 0.3
            self._add_to_nearest_water_body(world, space, surface_water)

    def _process_evaporation(self, world: World, dt: float) -> None:
        """水体蒸发"""
        for entity, (water,) in world.get_components(WaterBodyComponent):
            if water is None:
                continue

            # 蒸发量与温度、表面积相关
            evap = water.evaporation * dt
            water.volume = max(0.0, water.volume - evap)

            # 更新环境湿度
            env = world.get_component(entity, EnvironmentComponent)
            if env is not None:
                env.air_humidity = min(1.0, env.air_humidity + evap * 0.0001)

    def _process_infiltration_and_runoff(self, world: World, dt: float) -> None:
        """土壤渗透和径流"""
        for entity, (soil, groundwater) in world.get_components(
            SoilComponent, GroundwaterComponent
        ):
            if soil is None or groundwater is None:
                continue

            # 渗透：土壤水向地下水补给
            if soil.moisture > groundwater.porosity:
                excess = (soil.moisture - groundwater.porosity) * self.INFILTRATION_RATE * dt
                soil.moisture -= excess * 0.01
                groundwater.water_table += excess * 0.1

            # 径流：土壤饱和后流向水体
            if soil.moisture > self.RUNOFF_THRESHOLD:
                runoff = (soil.moisture - self.RUNOFF_THRESHOLD) * 0.5 * dt
                soil.moisture -= runoff * 0.01
                space = world.get_component(entity, SpaceComponent)
                if space is not None:
                    self._add_to_nearest_water_body(world, space, runoff * 10)

    def _process_groundwater_exchange(self, world: World, dt: float) -> None:
        """地下水与水体交换"""
        for entity, (groundwater,) in world.get_components(GroundwaterComponent):
            if groundwater is None:
                continue

            # 地下水向附近水体排泄
            if groundwater.water_table > -2.0:  # 地下水位较高
                discharge = self.GROUNDWATER_DISCHARGE * dt
                groundwater.water_table -= discharge * 0.1
                space = world.get_component(entity, SpaceComponent)
                if space is not None:
                    self._add_to_nearest_water_body(world, space, discharge * 100)

    def _process_river_flow(self, world: World, dt: float) -> None:
        """河流流动（上游向下游）"""
        for entity, (water,) in world.get_components(WaterBodyComponent):
            if water is None or water.body_type != "river":
                continue

            # 计算流出量
            if water.flow_rate > 0 and water.connected_to:
                outflow = water.flow_rate * dt
                water.volume = max(0.0, water.volume - outflow)

                # 分配到下游水体
                for downstream_id in water.connected_to:
                    downstream = world.query_entity(downstream_id)
                    if downstream is not None:
                        ds_water = world.get_component(downstream, WaterBodyComponent)
                        if ds_water is not None:
                            ds_water.volume = min(ds_water.max_volume, ds_water.volume + outflow / len(water.connected_to))

    def _add_to_nearest_water_body(self, world: World, space: SpaceComponent, amount: float) -> None:
        """将水量添加到最近的水体"""
        nearest = None
        nearest_dist = float('inf')

        for entity, (water, wb_space) in world.get_components(WaterBodyComponent, SpaceComponent):
            if water is None or wb_space is None:
                continue
            dist = ((space.x - wb_space.x) ** 2 + (space.y - wb_space.y) ** 2) ** 0.5
            if dist < nearest_dist and dist < 50:  # 50单位范围内
                nearest_dist = dist
                nearest = water

        if nearest is not None:
            nearest.volume = min(nearest.max_volume, nearest.volume + amount)
