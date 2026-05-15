#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:climate_system.py
@说明:气候系统 — 长期气候震荡（厄尔尼诺/拉尼娜/中性）
      继承 core.system.System 以适配环境管线
@时间:2026/05/16
@作者:Sherry
@版本:2.0
'''

import random

from core.world import World
from core.system import System
from environment.climate.climate_component import ClimateComponent


class ClimateSystem(System):
    """
    气候系统

    模拟 ENSO (厄尔尼诺-南方涛动) 对气候基线的长期调制:
    - Neutral:     无偏置 (rainfall_bias=0, humidity_bias=0)
    - ElNino:      降雨偏多 +0.3, 湿度偏大 +0.2
    - LaNina:      降雨偏少 -0.2, 湿度偏小 -0.1

    Input:  TimeComponent → 推进相位
    Output: ClimateComponent (rainfall_bias, humidity_bias, climate_phase)
    """

    PHASE_DURATION = (90, 400)  # 各阶段持续天数范围
    PHASES = ("Neutral", "ElNino", "LaNina")

    EL_NINO_RAIN = 0.3
    EL_NINO_HUMIDITY = 0.2
    LA_NINA_RAIN = -0.2
    LA_NINA_HUMIDITY = -0.1

    def update(self, world: World, delta_hours: float):
        climate = world._world_entity.get_component(ClimateComponent)
        if climate is None:
            return

        # 推进相位剩余天数
        climate.phase_remaining_days -= delta_hours / 24.0

        if climate.phase_remaining_days <= 0:
            # 过渡到新相位
            climate.climate_phase = random.choice(self.PHASES)
            climate.phase_remaining_days = random.uniform(*self.PHASE_DURATION)

        # 应用相位偏置
        if climate.climate_phase == "ElNino":
            climate.rainfall_bias = self.EL_NINO_RAIN
            climate.humidity_bias = self.EL_NINO_HUMIDITY
        elif climate.climate_phase == "LaNina":
            climate.rainfall_bias = self.LA_NINA_RAIN
            climate.humidity_bias = self.LA_NINA_HUMIDITY
        else:  # Neutral
            climate.rainfall_bias = 0.0
            climate.humidity_bias = 0.0
