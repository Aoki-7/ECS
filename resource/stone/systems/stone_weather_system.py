#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:stone_weather_system.py
@说明:石头风化系统
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.0
'''

from core.system import System
from core.world import World

from resource.stone.components.stone_component import StoneComponent


class StoneWeatherSystem(System):
    tick_interval = 20  # 每20帧执行一次

    def update(self, world: World, dt: float):
        for entity, [stone] in world.get_components(StoneComponent):
            stone: StoneComponent
            # 更新石头风化
            stone.update_weather(dt)