#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
污染扩散系统

v3.5 新增 — P1

职责：
    - 模拟污染物在空气/水/土壤中的扩散
    - 污染从污染源向周围传播
    - 与天气（风速、水流）交互

依赖：
    - PollutionComponent
    - EnvironmentComponent（风速、水流）
"""

import logging
from typing import Dict, List, Tuple

from core.system import System
from core.world import World

from environment.pollution.components.pollution_component import PollutionComponent
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class PollutionDiffusionSystem(System):
    """
    污染扩散系统

    每帧更新：
    1. 空气污染物随风扩散
    2. 水污染物随水流扩散
    3. 土壤污染物缓慢渗透
    4. 污染浓度自然衰减
    """

    tick_interval = 5  # 每5帧执行一次

    # 扩散参数
    AIR_DIFFUSION_RATE = 0.05    # 空气扩散速率
    WATER_DIFFUSION_RATE = 0.03  # 水扩散速率
    SOIL_DIFFUSION_RATE = 0.01   # 土壤扩散速率
    NATURAL_DECAY = 0.001        # 自然降解速率

    def update(self, world: World, dt: float) -> None:
        """更新污染扩散"""
        # 空气扩散
        self._diffuse_air_pollution(world, dt)

        # 水扩散
        self._diffuse_water_pollution(world, dt)

        # 土壤扩散
        self._diffuse_soil_pollution(world, dt)

        # 自然降解
        self._natural_decay(world, dt)

    def _diffuse_air_pollution(self, world: World, dt: float) -> None:
        """空气污染物随风扩散"""
        # 收集所有带污染的实体
        pollution_entities = []
        for entity, (pollution, space) in world.get_components(PollutionComponent, SpaceComponent):
            if pollution is None or space is None:
                continue
            if pollution.air_pollution > 0:
                pollution_entities.append((entity, pollution, space))

        # 扩散到附近实体
        for entity, pollution, space in pollution_entities:
            env = world.get_component(entity, EnvironmentComponent)
            wind_factor = env.wind_speed if env else 1.0

            # 扩散范围
            diffusion_range = 20 * wind_factor

            for other_entity, (other_pollution, other_space) in world.get_components(
                PollutionComponent, SpaceComponent
            ):
                if other_entity == entity or other_pollution is None:
                    continue

                dist = ((space.x - other_space.x) ** 2 + (space.y - other_space.y) ** 2) ** 0.5
                if dist > diffusion_range:
                    continue

                # 扩散量与距离成反比
                diffusion_amount = pollution.air_pollution * self.AIR_DIFFUSION_RATE * (1 - dist / diffusion_range) * dt

                # 污染源减少，目标增加
                pollution.air_pollution -= diffusion_amount
                other_pollution.air_pollution = min(1.0, other_pollution.air_pollution + diffusion_amount)

    def _diffuse_water_pollution(self, world: World, dt: float) -> None:
        """水污染物随水流扩散"""
        pollution_entities = []
        for entity, (pollution, space) in world.get_components(PollutionComponent, SpaceComponent):
            if pollution is None or space is None:
                continue
            if pollution.water_pollution > 0:
                pollution_entities.append((entity, pollution, space))

        for entity, pollution, space in pollution_entities:
            for other_entity, (other_pollution, other_space) in world.get_components(
                PollutionComponent, SpaceComponent
            ):
                if other_entity == entity or other_pollution is None:
                    continue

                dist = ((space.x - other_space.x) ** 2 + (space.y - other_space.y) ** 2) ** 0.5
                if dist > 15:  # 水扩散范围较小
                    continue

                diffusion_amount = pollution.water_pollution * self.WATER_DIFFUSION_RATE * (1 - dist / 15) * dt

                pollution.water_pollution -= diffusion_amount
                other_pollution.water_pollution = min(1.0, other_pollution.water_pollution + diffusion_amount)

    def _diffuse_soil_pollution(self, world: World, dt: float) -> None:
        """土壤污染物缓慢渗透"""
        pollution_entities = []
        for entity, (pollution, space) in world.get_components(PollutionComponent, SpaceComponent):
            if pollution is None or space is None:
                continue
            if pollution.soil_pollution > 0:
                pollution_entities.append((entity, pollution, space))

        for entity, pollution, space in pollution_entities:
            for other_entity, (other_pollution, other_space) in world.get_components(
                PollutionComponent, SpaceComponent
            ):
                if other_entity == entity or other_pollution is None:
                    continue

                dist = ((space.x - other_space.x) ** 2 + (space.y - other_space.y) ** 2) ** 0.5
                if dist > 5:  # 土壤扩散范围最小
                    continue

                diffusion_amount = pollution.soil_pollution * self.SOIL_DIFFUSION_RATE * (1 - dist / 5) * dt

                pollution.soil_pollution -= diffusion_amount
                other_pollution.soil_pollution = min(1.0, other_pollution.soil_pollution + diffusion_amount)

    def _natural_decay(self, world: World, dt: float) -> None:
        """污染自然降解"""
        for entity, (pollution,) in world.get_components(PollutionComponent):
            if pollution is None:
                continue

            # 所有污染类型都缓慢降解
            pollution.air_pollution = max(0.0, pollution.air_pollution - self.NATURAL_DECAY * dt)
            pollution.water_pollution = max(0.0, pollution.water_pollution - self.NATURAL_DECAY * dt)
            pollution.soil_pollution = max(0.0, pollution.soil_pollution - self.NATURAL_DECAY * dt)

            # 污染物浓度降解
            for pollutant_type in list(pollution.pollutants.keys()):
                pollution.pollutants[pollutant_type] = max(0.0, pollution.pollutants[pollutant_type] - self.NATURAL_DECAY * 10 * dt)
                if pollution.pollutants[pollutant_type] <= 0:
                    del pollution.pollutants[pollutant_type]
