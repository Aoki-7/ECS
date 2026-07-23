#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@文件:food_decay_system.py
@说明:食物腐败系统
@时间:2026/03/24 13:27:00
@作者:Sherry
@版本:1.1
'''

from core.system import System
from core.world import World

from resource.food.components.food_component import FoodComponent


class FoodDecaySystem(System):
    tick_interval = 20  # 每20帧执行一次

    @staticmethod
    def update_food_decay(food: FoodComponent, dt: float) -> None:
        """更新食物腐败"""
        if not food.is_perishable:
            return

        food.freshness -= food.decay_rate * dt
        if food.freshness < 0.0:
            food.freshness = 0.0

    def update(self, world: World, dt: float):
        for entity, [food] in world.get_components(FoodComponent):
            food: FoodComponent
            self.update_food_decay(food, dt)