


#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@文件: atmosphere_system.py
"""

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.weather.components.weather_component import WeatherComponent


# Climate
#    ↓
# Weather
#    ↓
# Atmosphere
#    ↓
# Wind
#    ↓
# LightField / Soil / Pollution

class AtmosphereSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    大气系统
    负责根据天气更新大气物理状态
    """

    def update(self, world: World, delta_hours: float) -> None:

        for entity, (atm, weather) in world.get_components(
            AtmosphereComponent,
            WeatherComponent
        ):

            atm: AtmosphereComponent
            weather: WeatherComponent

            self._update_air_density(atm, weather)
            self._update_pressure(atm, weather)

    def _update_air_density(self, atm: AtmosphereComponent, weather: WeatherComponent):
        """
        根据温度更新空气密度
        """

        T = weather.temperature + 273.15

        atm.air_density = 1.225 * (273.15 / T)

    def _update_pressure(self, atm: AtmosphereComponent, weather: WeatherComponent):
        """
        简化气压变化模型
        """

        base_pressure = 1013.25

        temp_effect = (weather.temperature - 15) * -0.8

        atm.pressure = base_pressure + temp_effect