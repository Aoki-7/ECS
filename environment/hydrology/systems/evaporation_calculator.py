#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蒸发计算器

职责：
    - 计算水体蒸发量
    - 考虑温度影响
"""

import logging

from environment.hydrology.components.water_body_component import WaterBodyComponent

logger = logging.getLogger(__name__)


class EvaporationCalculator:
    """蒸发计算器"""

    def __init__(self, base_rate: float = 0.001):
        self.base_rate = base_rate

    def calculate(self, water: WaterBodyComponent, temperature: float, dt: float) -> None:
        """
        计算蒸发量

        Args:
            water: 水体组件
            temperature: 温度 (°C)
            dt: 时间步长
        """
        # 温度影响：温度越高，蒸发越快
        temp_factor = max(0.0, (temperature - 5.0) / 30.0)  # 5°C 以下不蒸发

        # 计算蒸发量
        evaporation = self.base_rate * temp_factor * water.surface_area * dt
        evaporation = min(evaporation, water.volume)  # 不能超过现有水量

        # 更新水体
        water.volume -= evaporation
        water.evaporated_this_tick = evaporation

        # 更新水体状态
        if water.volume <= 0:
            water.is_dry = True
        else:
            water.is_dry = False
