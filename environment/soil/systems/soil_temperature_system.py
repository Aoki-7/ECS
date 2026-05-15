#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:soil_temperature_system.py
@说明:土壤温度变化系统
<<<<<<< HEAD
      已适配 PhysicalWeatherComponent（替代旧版 WeatherComponent）
@时间:2026/03/09 09:45:42
@作者:Sherry
@版本:2.0
'''

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
=======
@时间:2026/03/09 09:45:42
@作者:Sherry
@版本:1.0
'''


from environment.weather.components.weather_component import WeatherComponent
>>>>>>> 65a14767a91c763628f1030bcdd9bce57d718edc
from environment.soil.components.soil_temperature_component import SoilTemperatureComponent

from core.world import World
from core.system import System


class SoilTemperatureSystem(System):

    def update(self, world: World, delta_hours: float):

<<<<<<< HEAD
        weather, soil = world._world_entity.get_components(
            PhysicalWeatherComponent, SoilTemperatureComponent
        )
        weather: PhysicalWeatherComponent
        soil: SoilTemperatureComponent

        soil.temperature = soil.temperature * 0.9 + weather.temperature * 0.1
=======
        weather, soil = world._world_entity.get_components(WeatherComponent, SoilTemperatureComponent)
        weather: WeatherComponent
        soil: SoilTemperatureComponent


        soil.temperature = soil.temperature * 0.9 + weather.temperature * 0.1
>>>>>>> 65a14767a91c763628f1030bcdd9bce57d718edc
