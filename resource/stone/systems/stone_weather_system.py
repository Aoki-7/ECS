#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@文件:stone_weather_system.py
@说明:石头风化系统
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.1
'''

from core.system import System
from core.world import World

from resource.stone.components.stone_component import StoneComponent


class StoneWeatherSystem(System):
    tick_interval = 20  # 每20帧执行一次

    @staticmethod
    def update_weathering(stone: StoneComponent, dt: float) -> None:
        """更新石头风化"""
        stone.weathering += stone.weathering_rate * dt
        if stone.weathering > 1.0:
            stone.weathering = 1.0

    def update(self, world: World, dt: float):
        for entity, [stone] in world.get_components(StoneComponent):
            stone: StoneComponent
            self.update_weathering(stone, dt)
