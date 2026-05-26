#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:food_clean_up_system.py
@说明:食物清理系统
@时间:2026/03/25 11:59:24
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World
from core.entity import Entity
from typing import List

from resource.food.components.food_component import FoodComponent


class FoodCleanupSystem(System):
    """
    食物清理系统

    ===== 职责 =====
    - 判断食物是否应该从世界中移除
    - 统一回收（避免各处手动删除）

    ===== 设计原则 =====
    - 不修改 FoodComponent 内部逻辑
    - 只做“判定 + 移除”
    """

    def __init__(self,
                 remove_if_empty: bool = True,
                 remove_if_spoiled: bool = False):
        """
        Args:
            remove_if_empty: 吃完是否删除
            remove_if_spoiled: 腐败是否删除（可选）
        """
        self.remove_if_empty = remove_if_empty
        self.remove_if_spoiled = remove_if_spoiled

    def update(self, world: World, dt: float):
        to_remove: List[Entity] = []

        # 遍历所有带 FoodComponent 的实体
        for entity in world.get_entities_with(FoodComponent):
            food: FoodComponent = world.get_component(entity, FoodComponent)

            if food is None:
                continue

            # ===== 判定逻辑 =====
            should_remove = False

            # 1. 吃完
            if self.remove_if_empty and food.is_empty():
                should_remove = True

            # 2. 腐败（可选策略）
            elif self.remove_if_spoiled and food.is_spoiled():
                should_remove = True

            if should_remove:
                to_remove.append(entity)

        # ===== 批量删除（避免遍历时修改容器）=====
        for entity in to_remove:
            world.remove_entity(entity)