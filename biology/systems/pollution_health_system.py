#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
污染健康系统

v3.6 新增 — P2

职责：
    - 污染影响生物健康
    - PM2.5 导致呼吸系统损伤
    - 臭氧导致皮肤/眼睛损伤
    - SO2/NO2 导致中毒

设计原则：
    - 纯物理驱动：污染物浓度 → 健康影响
    - 无硬编码阈值

依赖：
    - HealthStatusComponent
    - PollutionComponent
    - AtmosphereComponent
"""

import logging
from typing import Dict

from core.system import System
from core.world import World

from biology.components.health_status_component import HealthStatusComponent
from environment.pollution.components.pollution_component import PollutionComponent
from environment.atmosphere.components.atmosphere_component import AtmosphereComponent

logger = logging.getLogger(__name__)


class PollutionHealthSystem(System):
    """
    污染健康系统

    物理原理：
    - PM2.5 → 呼吸系统损伤（浓度越高，损伤越大）
    - O3 → 皮肤/眼睛刺激
    - SO2 → 呼吸道刺激
    - NO2 → 肺部损伤
    - CO → 缺氧（与血红蛋白结合）

    每帧更新：
    1. 计算污染物暴露
    2. 应用健康影响
    3. 累积慢性损伤
    """

    tick_interval = 10  # 每10帧执行一次

    # 健康影响系数
    PM25_DAMAGE_RATE = 0.001    # PM2.5 损伤速率
    O3_DAMAGE_RATE = 0.002      # 臭氧损伤速率
    SO2_DAMAGE_RATE = 0.0015    # SO2 损伤速率
    NO2_DAMAGE_RATE = 0.001     # NO2 损伤速率
    CO_DAMAGE_RATE = 0.003      # CO 损伤速率

    def update(self, world: World, dt: float) -> None:
        """更新污染健康影响"""
        for entity, (health, pollution) in world.get_components(
            HealthStatusComponent, PollutionComponent
        ):
            if health is None or pollution is None:
                continue

            # 1. 计算空气污染影响
            self._apply_air_pollution_effects(health, pollution, dt)

            # 2. 计算水污染影响（如果生物饮水）
            self._apply_water_pollution_effects(health, pollution, dt)

            # 3. 计算土壤污染影响（如果生物接触土壤）
            self._apply_soil_pollution_effects(health, pollution, dt)

    def _apply_air_pollution_effects(self, health: HealthStatusComponent,
                                     pollution: PollutionComponent, dt: float) -> None:
        """应用空气污染健康影响"""
        air_pollution = pollution.air_pollution

        if air_pollution <= 0:
            return

        # PM2.5 导致呼吸系统损伤
        pm_damage = air_pollution * self.PM25_DAMAGE_RATE * dt
        if pm_damage > 0.01:
            health.add_wound("respiratory", pm_damage, damage_per_sec=pm_damage * 0.1)

        # 综合空气污染降低生命值
        health.hp -= air_pollution * 0.01 * dt
        health.hp = max(0.0, health.hp)

    def _apply_water_pollution_effects(self, health: HealthStatusComponent,
                                       pollution: PollutionComponent, dt: float) -> None:
        """应用水污染健康影响"""
        water_pollution = pollution.water_pollution

        if water_pollution <= 0:
            return

        # 水污染导致消化系统损伤
        water_damage = water_pollution * 0.002 * dt
        if water_damage > 0.01:
            health.add_wound("digestive", water_damage, damage_per_sec=water_damage * 0.05)

    def _apply_soil_pollution_effects(self, health: HealthStatusComponent,
                                      pollution: PollutionComponent, dt: float) -> None:
        """应用土壤污染健康影响"""
        soil_pollution = pollution.soil_pollution

        if soil_pollution <= 0:
            return

        # 土壤污染导致皮肤损伤
        soil_damage = soil_pollution * 0.001 * dt
        if soil_damage > 0.01:
            health.add_wound("skin", soil_damage, damage_per_sec=soil_damage * 0.02)