#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
极端天气事件生成系统 — 从 old weather/ 迁移至 physics_weather/

根据概率生成极端天气事件（寒潮/热浪/风暴/干旱/台风/暴雪），
创建携带 WeatherModifierComponent 的事件实体，
由 WeatherModifierBridgeSystem 将修正量写入 PhysicalWeatherComponent。
"""

import random

from core.world import World
from core.system import System
from environment.season.season_component import SeasonComponent, Season
from environment.physics_weather.components.weather_event_components import (
    WeatherEventTagComponent,
)
from environment.physics_weather.systems.weather_event_factory import (
    WeatherEventFactory,
)


class WeatherEventSystem(System):
    """极端天气事件生成系统"""

    def __init__(self, world: World, event_probability_per_hour: float = 0.002):
        self.factory = WeatherEventFactory(world)
        self.event_probability = event_probability_per_hour

    def update(self, world: World, delta_hours: float):
        # 1. 检查当前是否存在进行中的极端天气
        active_events = list(world.get_components(WeatherEventTagComponent))
        if active_events:
            for entity, [w_comp] in active_events:
                w_comp: WeatherEventTagComponent
                print("当前存", w_comp.name)
            return  # 已有极端天气，不生成新事件

        # 2. 按概率生成
        prob = self.event_probability * delta_hours

        season: SeasonComponent = world._world_entity.get_component(SeasonComponent)
        if season and season.season == Season.SUMMER:
            prob *= 5.0  # 夏季极端天气概率 x5

        if random.random() < prob:
            weather_event = self.factory.create_random_event()
            tag = world.get_component(weather_event, WeatherEventTagComponent)
            print("极端天气产生了！类型：", tag.name if tag else "unknown")
