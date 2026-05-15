#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:soil_temperature_system.py
@说明:土壤温度变化系统
@时间:2026/03/09 09:45:42
@作者:Sherry
@版本:1.0
'''


from environment.weather.components.weather_component import WeatherComponent
from environment.soil.components.soil_temperature_component import SoilTemperatureComponent

from core.world import World
from core.system import System


class SoilTemperatureSystem(System):

    def update(self, world: World, delta_hours: float):

        weather, soil = world._world_entity.get_components(WeatherComponent, SoilTemperatureComponent)
        weather: WeatherComponent
        soil: SoilTemperatureComponent


        soil.temperature = soil.temperature * 0.9 + weather.temperature * 0.1