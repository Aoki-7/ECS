#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:soil_system.py
@说明:土壤系统 — 修复硬编码温度、移除与SoilWaterBalanceSystem冲突的湿度逻辑
      从 EnvironmentComponent（已由天气同步）读取气温和降水数据。
      湿度管理移交 SoilWaterBalanceSystem 统一处理。
      本系统仅负责养分循环和pH变化。
@时间:2026/05/16
@作者:Sherry
@版本:2.0
"""

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent


class SoilSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    土壤系统

    负责更新土壤状态（不含湿度——由 SoilWaterBalanceSystem 管理）：
    - 温度跟随环境温度
    - 养分循环（消耗/释放）
    - pH值自然变化
    """

    def __init__(self):
        super().__init__()
        self.priority = 10

    def update(self, world: World, delta_hours: float):
        # 获取当前环境数据
        env = world._world_entity.get_component(EnvironmentComponent)
        weather_temp = env.air_temperature if env else 20.0

        for entity, (soil,) in world.get_components(SoilComponent):
            self._update_soil(soil, weather_temp, delta_hours)

    def _update_soil(self, soil: SoilComponent, weather_temp: float, delta_hours: float):
        # ---- 1. 土壤温度（跟随环境气温，一阶滞后） ----
        temp_change_rate = 0.1 * delta_hours
        soil.temperature += (weather_temp - soil.temperature) * temp_change_rate

        # ---- 2. 养分自然消耗 ----
        nutrient_decay = 0.001 * delta_hours
        soil.nitrogen *= (1 - nutrient_decay)
        soil.phosphorus *= (1 - nutrient_decay)
        soil.potassium *= (1 - nutrient_decay)

        # ---- 3. pH值自然趋向中性 ----
        ph_change_rate = 0.01 * delta_hours
        if soil.ph < 7.0:
            soil.ph = min(7.0, soil.ph + ph_change_rate)
        elif soil.ph > 7.0:
            soil.ph = max(7.0, soil.ph - ph_change_rate)
