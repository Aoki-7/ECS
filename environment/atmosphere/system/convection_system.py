#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:convection_system.py
@说明:对流系统 — 基于 PhysicalWeather 计算对流参数
      已适配 PhysicalWeatherComponent（替代旧版 WeatherComponent）
@时间:2026/03/07 11:35:57
@作者:Sherry
@版本:2.0
'''

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)


class ConvectionSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    对流系统

    从 PhysicalWeatherComponent 读取温度，
    计算对流强度和湍流，同步到 AtmosphereComponent。
    """

    def update(self, world: World, delta_hours: float):
        # 防御：使用 world.get_world_component 替代 entity.get_component
        atm = world.get_world_component(AtmosphereComponent)
        weather = world.get_world_component(PhysicalWeatherComponent)

        if atm is None or weather is None:
            return

        temp = weather.temperature

        # 温度越高，对流越强（基准温度 20°C）
        convection = max(0, temp - 20) * 0.1

        # 湿度增强对流（湿空气对流更强烈）
        rh_boost = max(0, weather.relative_humidity - 0.6) * 0.5 if weather.relative_humidity > 0.6 else 0

        atm.convection_strength = round(convection + rh_boost, 4)

        # 湍流强度，与对流和风速相关
        wind_boost = weather.wind_speed * 0.02
        atm.turbulence = round((convection + rh_boost) * 0.5 + wind_boost, 4)
