#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:soil_water_balance_system.py
@说明:土壤水分平衡系统
      已适配 PhysicalWeatherComponent（替代旧版 WeatherComponent）
@时间:2026/03/09 09:34:33
@作者:Sherry
@版本:2.0
"""

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.soil.components.soil_moisture_component import SoilMoistureComponent

from core.world import World
from core.system import System


class SoilWaterBalanceSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    土壤水分平衡系统
    负责：
    - 降雨补给（来自 PhysicalWeatherComponent.precipitation_rate）
    - 蒸发（基于 PhysicalWeatherComponent.temperature 简化计算）
    - 自然流失
    """
    def update(self, world: World, delta_hours: float):

        weather, soil = world._world_entity.get_components(
            PhysicalWeatherComponent, SoilMoistureComponent,
        )

        weather: PhysicalWeatherComponent
        soil: SoilMoistureComponent

        # 降雨补给 (mm/h → 土壤湿度增量)
        soil.moisture += weather.precipitation_rate * 0.1 * delta_hours

        # 蒸发 (温度越高, 蒸发越快)
        soil.moisture -= weather.temperature * 0.001 * delta_hours

        soil.moisture = max(0.0, min(soil.moisture, soil.capacity))
