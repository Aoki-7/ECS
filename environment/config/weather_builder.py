#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""天气模块构建器"""


from core.world import World


class WeatherBuilder:

    @staticmethod
    def build(world: World):
        """
        构建天气组件和系统
        
        Args:
            world: 当前世界实例
            
        Returns:
            构建的天气系统列表
        """
        # 添加基础物理天气组件
        from environment.physics_weather.components.physical_weather_component import (
            PhysicalWeatherComponent,
        )
        world._world_entity.add_component(PhysicalWeatherComponent())
        
        # 添加大气模块
        from environment.weather.systems.atmosphere import AtmosphereSystem
        atmosphere_system = AtmosphereSystem.create()
        
        # 添加气候系统
        from environment.weather.systems.climate import ClimateSystem
        climate_system = ClimateSystem.create()
        
        return [atmosphere_system, climate_system]