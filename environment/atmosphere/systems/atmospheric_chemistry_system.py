#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大气化学系统

v3.6 新增 — P1

职责：
    - 模拟大气化学成分变化
    - 污染物反应、臭氧生成、PM2.5累积
    - 与污染系统联动

设计原则：
    - 纯化学反应驱动
    - 无硬编码阈值
"""

import logging
from typing import Dict

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.pollution.components.pollution_component import PollutionComponent

logger = logging.getLogger(__name__)


class AtmosphericChemistrySystem(System):
    """
    大气化学系统

    化学反应：
    - NO2 + 阳光 → O3（光化学反应）
    - SO2 + H2O → H2SO4（酸雨前体）
    - CO + OH → CO2（氧化）
    - PM2.5 累积/沉降

    每帧更新：
    1. 光化学反应
    2. 氧化反应
    3. 颗粒物动力学
    4. 扩散稀释
    """

    tick_interval = 10

    # 反应速率常数（简化）
    PHOTOLYSIS_RATE = 0.001       # NO2光解速率
    OXIDATION_RATE = 0.0005       # CO氧化速率
    PM_FORMATION_RATE = 0.01      # PM2.5形成速率
    PM_DEPOSITION_RATE = 0.001    # PM2.5沉降速率

    def update(self, world: World, dt: float) -> None:
        """更新大气化学"""
        for entity, (atmos, pollution) in world.get_components(
            AtmosphereComponent, PollutionComponent
        ):
            if atmos is None:
                continue

            # 1. 光化学反应（需要阳光）
            self._photochemical_reactions(atmos, dt)

            # 2. 氧化反应
            self._oxidation_reactions(atmos, dt)

            # 3. 颗粒物动力学
            self._particulate_dynamics(atmos, pollution, dt)

            # 4. 与污染系统同步
            self._sync_with_pollution(atmos, pollution)

    def _photochemical_reactions(self, atmos: AtmosphereComponent, dt: float) -> None:
        """光化学反应：NO2 + 阳光 → O3"""
        # 简化的光化学模型
        # O3 生成 ∝ NO2 × 光强
        light_intensity = max(0.0, atmos.temperature / 30.0)  # 温度作为光强代理
        
        o3_formation = atmos.no2_ppm * light_intensity * self.PHOTOLYSIS_RATE * dt
        atmos.o3_ppm += o3_formation
        atmos.no2_ppm = max(0.0, atmos.no2_ppm - o3_formation * 0.5)

        # O3 自然分解
        o3_decay = atmos.o3_ppm * 0.0001 * dt
        atmos.o3_ppm = max(0.0, atmos.o3_ppm - o3_decay)

    def _oxidation_reactions(self, atmos: AtmosphereComponent, dt: float) -> None:
        """氧化反应：CO + OH → CO2"""
        # CO 氧化为 CO2
        co_oxidized = atmos.co_ppm * self.OXIDATION_RATE * dt
        atmos.co_ppm = max(0.0, atmos.co_ppm - co_oxidized)
        atmos.co2_ratio += co_oxidized * 1e-6  # ppm → 比例

    def _particulate_dynamics(self, atmos: AtmosphereComponent,
                              pollution: PollutionComponent, dt: float) -> None:
        """颗粒物动力学"""
        if pollution is None:
            return

        # PM2.5 形成（来自气态污染物）
        pm_formation = (atmos.so2_ppm + atmos.no2_ppm) * self.PM_FORMATION_RATE * dt
        atmos.pm25 += pm_formation * 10  # 转换为 μg/m³

        # PM2.5 沉降
        pm_deposition = atmos.pm25 * self.PM_DEPOSITION_RATE * dt
        atmos.pm25 = max(0.0, atmos.pm25 - pm_deposition)

        # PM10 包含 PM2.5 + 粗颗粒
        atmos.pm10 = atmos.pm25 * 1.5  # 简化关系

    def _sync_with_pollution(self, atmos: AtmosphereComponent,
                             pollution: PollutionComponent) -> None:
        """与污染系统同步"""
        if pollution is None:
            return

        # 将大气化学数据同步到污染系统
        # 计算综合空气污染指数
        aqi = (
            atmos.pm25 * 0.4 +
            atmos.pm10 * 0.2 +
            atmos.o3_ppm * 100 * 0.2 +
            atmos.no2_ppm * 100 * 0.1 +
            atmos.so2_ppm * 100 * 0.1
        )

        # 归一化到 0-1
        pollution.air_pollution = min(1.0, aqi / 500.0)