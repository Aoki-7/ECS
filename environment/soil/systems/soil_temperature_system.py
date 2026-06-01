#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:soil_temperature_system.py
@说明:土壤温度变化系统
      已适配 PhysicalWeatherComponent（替代旧版 WeatherComponent）
@时间:2026/03/09 09:45:42
@作者:Sherry
@版本:2.0
"""

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.soil.components.soil_temperature_component import SoilTemperatureComponent

from core.world import World
from core.system import System


class SoilTemperatureSystem(System):
    tick_interval = 2  # 每2帧执行一次

    def update(self, world: World, delta_hours: float):

        weather, soil = world._world_entity.get_components(
            PhysicalWeatherComponent, SoilTemperatureComponent
        )
        weather: PhysicalWeatherComponent
        soil: SoilTemperatureComponent

        soil.temperature = soil.temperature * 0.9 + weather.temperature * 0.1
