#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:food_decay_system.py
@说明:食物腐败系统
@时间:2026/03/24 13:27:00
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World

from resource.food.components.food_component import FoodComponent


class FoodDecaySystem(System):
    tick_interval = 20  # 每20帧执行一次

    def update(self, world: World, dt: float):
        for entity, [food] in world.get_components(FoodComponent):
            food: FoodComponent
            # 更新食物腐败
            food.update_decay(dt)