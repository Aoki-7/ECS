#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:physics_weather_builder.py
@说明:物理天气系统构建器
      挂载 PhysicalWeatherComponent + PhysicalWeatherSystem + 极端天气系统
@时间:2026/05/16
@作者:Sherry
@版本:3.0
'''

from core.world import World

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.physics_weather.systems.physical_weather_system import (
    PhysicalWeatherSystem,
)
from environment.physics_weather.systems.weather_modifier_bridge import (
    WeatherModifierBridgeSystem,
)
from environment.physics_weather.systems.weather_event_system import (
    WeatherEventSystem,
)


class PhysicsWeatherBuilder:
    """
    物理天气系统构建器

    负责：
    1. 挂载 PhysicalWeatherComponent（世界级）
    2. 注册 PhysicalWeatherSystem（物理量自然演化）
    3. 注册 WeatherModifierBridgeSystem（极端天气→物理量桥接）
    4. 注册 WeatherEventSystem（极端天气事件生成）
    """

    @staticmethod
    def build(world: World, profile=None):
        # 挂载物理天气组件
        world.get_world_entity().add_component(PhysicalWeatherComponent())

        # 参数提取
        latitude = getattr(profile, 'latitude', 35.0) if profile else 35.0
        elevation = getattr(profile, 'elevation', 0.0) if profile else 0.0

        # 创建系统
        weather_system = PhysicalWeatherSystem(
            latitude=latitude,
            elevation=elevation,
        )
        modifier_bridge = WeatherModifierBridgeSystem()
        event_system = WeatherEventSystem()

        return [weather_system, modifier_bridge, event_system]