#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
洋流系统

v3.5 新增 — P1

职责：
    - 模拟洋流运动
    - 暖流/寒流影响周围温度
    - 与大气交互（厄尔尼诺效应）

依赖：
    - OceanCurrentComponent
    - EnvironmentComponent
"""

import logging
import math
from typing import Dict, List

from core.system import System
from core.world import World

from environment.ocean.components.ocean_current_component import OceanCurrentComponent
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class OceanCurrentSystem(System):
    """
    洋流系统

    每帧更新：
    1. 洋流速度变化
    2. 暖流加热周围空气
    3. 寒流冷却周围空气
    4. 盐度平衡
    """

    tick_interval = 10  # 每10帧执行一次

    # 洋流参数
    TEMPERATURE_INFLUENCE_RANGE = 30  # 温度影响范围
    WARM_CURRENT_TEMP_BOOST = 0.5     # 暖流升温
    COLD_CURRENT_TEMP_DROP = 0.5      # 寒流降温

    def update(self, world: World, dt: float) -> None:
        """更新洋流"""
        # 洋流影响周围温度
        self._influence_temperature(world, dt)

        # 盐度平衡
        self._balance_salinity(world, dt)

    def _influence_temperature(self, world: World, dt: float) -> None:
        """洋流影响周围空气温度"""
        for entity, (current, space) in world.get_components(
            OceanCurrentComponent, SpaceComponent
        ):
            if current is None or space is None:
                continue

            # 影响范围
            influence_range = self.TEMPERATURE_INFLUENCE_RANGE

            for other_entity, (env, other_space) in world.get_components(
                EnvironmentComponent, SpaceComponent
            ):
                if other_entity == entity or env is None or other_space is None:
                    continue

                dist = ((space.x - other_space.x) ** 2 + (space.y - other_space.y) ** 2) ** 0.5
                if dist > influence_range:
                    continue

                # 影响强度与距离成反比
                influence = (1 - dist / influence_range) * dt

                if current.current_type == "warm":
                    env.air_temperature += self.WARM_CURRENT_TEMP_BOOST * influence
                elif current.current_type == "cold":
                    env.air_temperature -= self.COLD_CURRENT_TEMP_DROP * influence

    def _balance_salinity(self, world: World, dt: float) -> None:
        """盐度平衡（高盐度向低盐度扩散）"""
        currents = []
        for entity, (current, space) in world.get_components(
            OceanCurrentComponent, SpaceComponent
        ):
            if current is None or space is None:
                continue
            currents.append((entity, current, space))

        for i, (entity1, current1, space1) in enumerate(currents):
            for entity2, current2, space2 in currents[i+1:]:
                dist = ((space1.x - space2.x) ** 2 + (space1.y - space2.y) ** 2) ** 0.5
                if dist > 20:
                    continue

                # 盐度平衡
                avg_salinity = (current1.salinity + current2.salinity) / 2
                diff1 = (avg_salinity - current1.salinity) * 0.01 * dt
                diff2 = (avg_salinity - current2.salinity) * 0.01 * dt

                current1.salinity += diff1
                current2.salinity += diff2
