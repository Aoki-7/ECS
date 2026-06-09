#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
衣物系统

v3.0.1 新增 — P1

职责：
    - 更新衣物耐久度（磨损）
    - 计算实体总保暖值
    - 处理湿度和晾干
    - 温度适应
"""

from core.system import System
from core.world import World

from human.components.clothing_component import ClothingComponent, OutfitComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from environment.environment_component import EnvironmentComponent

import logging

logger = logging.getLogger(__name__)


class ClothingSystem(System):
    """
    衣物系统

    管理衣物的耐久度、保暖效果和温度适应。
    """

    tick_interval = 10

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新衣物状态"""
        env = world.get_environment()
        if env is None:
            return

        temp = env.air_temperature
        humidity = env.air_humidity
        rainfall = getattr(env, "rainfall", 0.0)

        for entity, (outfit, needs) in world.get_components(
            OutfitComponent, PhysiologyNeedsComponent
        ):
            self._update_outfit(world, entity, outfit, needs, temp, humidity, rainfall, dt)

    def _update_outfit(
        self, world, entity, outfit, needs,
        temp: float, humidity: float, rainfall: float, dt: float
    ) -> None:
        """更新单个实体的着装"""
        total_insulation = 0.0

        for clothing_type, clothing_id in list(outfit.worn_items.items()):
            clothing_entity = world.query_entity(clothing_id)
            if clothing_entity is None:
                continue

            clothing = world.get_component(clothing_entity, ClothingComponent)
            if clothing is None:
                continue

            # 磨损
            clothing.wear(0.005 * dt)

            # 下雨变湿
            if rainfall > 0.0:
                clothing.get_wet(rainfall * 0.01 * dt)

            # 晾干
            if humidity < 0.5 and clothing.wetness > 0.0:
                clothing.dry(0.02 * dt)

            # 计算有效保暖
            effective = clothing.calculate_effective_insulation()
            total_insulation += effective

            # 破损衣物移除
            if clothing.durability <= 0.0:
                outfit.remove_item(clothing_type)
                logger.debug(f"[Clothing] E{entity.id} 的 {clothing_type} 已破损")

        outfit.total_insulation = total_insulation

        # 温度适应
        self._apply_temperature_effects(entity, needs, temp, total_insulation)

    def _apply_temperature_effects(
        self, entity, needs, temp: float, insulation: float
    ) -> None:
        """应用温度效果"""
        # 舒适温度范围
        comfort_low = 18.0
        comfort_high = 26.0

        # 有效温度 = 环境温度 - 保暖值
        effective_temp = temp + insulation

        if effective_temp < comfort_low:
            # 寒冷
            cold_stress = (comfort_low - effective_temp) / 10.0
            needs.energy = max(0.0, getattr(needs, "energy", 100.0) - cold_stress * 0.5)
        elif effective_temp > comfort_high:
            # 炎热
            heat_stress = (effective_temp - comfort_high) / 10.0
            needs.energy = max(0.0, getattr(needs, "energy", 100.0) - heat_stress * 0.3)
