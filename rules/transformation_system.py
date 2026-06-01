#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:transformation_system.py
@说明:通用状态转换系统
@时间:2026/03/26 13:22:45
@作者:Sherry
@版本:1.0
'''


from core.system import System
from core.world import World
from core.entity import Entity
from typing import List

from resource.food.components.food_component import FoodComponent


class TransformationSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    通用状态转换系统

    ===== 职责 =====
    - 根据规则执行实体状态转换
    - 不关心具体业务（完全数据驱动）
    """

    def __init__(self, rules: List):
        self.rules = rules

    def update(self, world: World, dt: float):

        # 按规则逐个执行
        for rule in self.rules:

            for entity, [comp] in world.get_components(rule.source_component):

                if comp is None:
                    continue

                if rule.condition(comp):
                    rule.transform(entity, world)

