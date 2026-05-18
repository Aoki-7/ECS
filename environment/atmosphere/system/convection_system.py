



#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:convection_system.py
@说明:对流系统，温度差引起的空气流动，影响风场和热交换
      已适配 PhysicalWeatherComponent（替代旧版 WeatherComponent）
@时间:2026/03/07 11:35:57
@作者:Sherry
@版本:2.0
@时间:2026/03/07 11:35:57
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.weather.components.weather_component import WeatherComponent


class ConvectionSystem(System):
    """
    对流风系统，影响风场和热交换

    从 PhysicalWeatherComponent 读取温度以计算对流强度。
    """
    def update(self, world: World, delta_hours: float):

        for entity, [atm, weather] in world.get_components(
            AtmosphereComponent,
            PhysicalWeatherComponent,
        ):
            atm: AtmosphereComponent
            weather: PhysicalWeatherComponent

            temp = weather.temperature

            convection = max(0, temp - 20) * 0.1  # 温度越高，对流越强

            atm.convection_strength = convection   # 对流强度

            atm.turbulence = convection * 0.5       # 湍流强度，影响云形成和降水
            WeatherComponent
        ):
            atm: AtmosphereComponent
            weather: WeatherComponent

            temp = weather.temperature

            convection = max(0, temp - 20) * 0.1 # 温度越高，对流越强

            atm.convection_strength = convection # 对流强度

            atm.turbulence = convection * 0.5 # 湍流强度，影响云形成和降水
