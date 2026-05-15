

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:weather_builder.py
@说明:天气系统构建器，负责根据天气配置表创建天气组件并初始化状态
@时间:2026/03/08 11:22:13
@作者:Sherry
@版本:1.0
'''


from core.world import World

from environment.weather.components.weather_component import WeatherComponent

from environment.weather.systems.weather_system import WeatherSystem
from environment.weather.systems.weather_event_system import WeatherEventSystem


class WeatherBuilder:
    @staticmethod
    def build(world: World, profile = None):
        """
        根据天气配置表创建天气组件并初始化状态
        """
        world._world_entity.add_component(WeatherComponent())

        event_system = WeatherEventSystem(world)
        weather_system = WeatherSystem()

        weather_systems = [event_system, weather_system]

        return weather_systems
