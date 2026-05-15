#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:weather_event_factory.py
@说明: 极端天气事件工厂 — 从 old weather/ 迁移至 physics_weather/
@时间:2026/05/16
@作者:Sherry
@版本:2.0
'''

import random

from core.world import World
from environment.physics_weather.components.weather_event_components import (
    WeatherEventTagComponent,
    ExtremeWeatherLifetimeComponent,
    WeatherModifierComponent,
    WeatherEventType,
)

LifetimeComponent = ExtremeWeatherLifetimeComponent


class WeatherEventTemplates:
    """
    极端天气事件模板

    每个模板定义：
    - duration: 持续时间范围（小时）
    - temp: 温度变化范围（摄氏度）
    - humidity: 绝对湿度变化范围 (g/m³)
    - rainfall: 降水速率变化范围 (mm/h)
    """
    TEMPLATES = {
        "cold_wave": {
            "duration": (6, 24),
            "temp": (-10.0, -3.0),
            "humidity": (0.0, 2.0),
            "rainfall": (0.0, 2.0),
        },
        "heat_wave": {
            "duration": (6, 24),
            "temp": (3.0, 10.0),
            "humidity": (-4.0, 0.0),
            "rainfall": (0.0, 1.0),
        },
        "storm": {
            "duration": (3, 12),
            "temp": (-2.0, 2.0),
            "humidity": (3.0, 8.0),
            "rainfall": (5.0, 20.0),
        },
        "drought": {
            "duration": (24, 72),
            "temp": (2.0, 6.0),
            "humidity": (-8.0, -3.0),
            "rainfall": (-5.0, -1.0),
        },
        "typhoon": {
            "duration": (3, 18),
            "temp": (-1.0, 1.0),
            "humidity": (5.0, 10.0),
            "rainfall": (10.0, 50.0),
        },
        "snowstorm": {
            "duration": (3, 12),
            "temp": (-15.0, -5.0),
            "humidity": (1.0, 4.0),
            "rainfall": (3.0, 10.0),
        },
    }


class WeatherEventFactory:

    def __init__(self, world: World):
        self.world = world

    def create_event(self, event_type: str):
        if event_type not in WeatherEventTemplates.TEMPLATES:
            raise ValueError(f"Unknown weather event type: {event_type}")

        tpl = WeatherEventTemplates.TEMPLATES[event_type]

        duration = random.uniform(*tpl["duration"])
        temp_delta = random.uniform(*tpl["temp"])
        humidity_delta = random.uniform(*tpl["humidity"])
        rainfall_delta = random.uniform(*tpl["rainfall"])

        entity = self.world.create_entity()

        self.world.add_component(
            entity,
            WeatherEventTagComponent(event_type=WeatherEventType(event_type)),
        )
        self.world.add_component(
            entity,
            WeatherModifierComponent(
                duration_hours=duration,
                temp_delta=temp_delta,
                humidity_delta=humidity_delta,
                rainfall_delta=rainfall_delta,
            ),
        )
        self.world.add_component(
            entity,
            LifetimeComponent(remaining_hours=duration),
        )

        return entity

    def create_random_event(self):
        event_type = random.choice(list(WeatherEventTemplates.TEMPLATES.keys()))
        return self.create_event(event_type)

    def spawn_batch(self, count: int):
        if count <= 0:
            raise ValueError("Batch count must be positive.")
        return [self.create_random_event() for _ in range(count)]
