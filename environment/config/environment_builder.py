







#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
环境构建器

作用：
    根据 EnvironmentProfile
    自动为世界创建所有环境组件
"""


from core.world import World


from environment.weather.config.weather_builder import WeatherBuilder
from environment.season.config.season_builder import SeasonBuilder
from environment.observation.environment_observation_component import EnvironmentObservationComponent

class EnvironmentBuilder:

    @staticmethod
    def build(world: World, profile = None):
        
        world._world_entity.add_component(EnvironmentObservationComponent())
        
        # 1️⃣ 构建天气组件和系统
        weather_systems = WeatherBuilder.build(world, profile)
        # 2️⃣ 构建季节组件和系统
        season_systems = SeasonBuilder.build(world, profile)

        env_system = []
        env_system.extend(season_systems)
        env_system.extend(weather_systems)
        
        return env_system