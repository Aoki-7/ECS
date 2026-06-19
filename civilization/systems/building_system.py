#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建筑系统

提供 BuildingComponent 和 BuildingInventoryComponent 的静态操作方法。
"""

from core.system import System
from core.world import World
from civilization.components.building_component import BuildingComponent, BuildingInventoryComponent


class BuildingSystem(System):
    """建筑系统 - ECS System 版本"""
    tick_interval = 1
    priority = 60

    def update(self, world: World, dt: float = 1.0):
        """遍历所有建筑实体，执行耐久度衰减"""
        for entity, (building,) in world.get_components(BuildingComponent):
            # 建筑自然老化
            if building.is_active:
                building.durability = max(0.0, building.durability - 0.01 * dt)
                if building.durability <= 0:
                    building.is_active = False

    @staticmethod
    def take_damage(building: BuildingComponent, damage: float) -> None:
        """受到损伤"""
        building.durability = max(0.0, building.durability - damage)
        if building.durability <= 0:
            building.is_active = False

    @staticmethod
    def repair(building: BuildingComponent, amount: float) -> None:
        """修复建筑"""
        building.durability = min(building.max_durability, building.durability + amount)
        if building.durability > 0:
            building.is_active = True

    @staticmethod
    def add_occupant(building: BuildingComponent, entity_id: int) -> bool:
        """添加 occupants"""
        if len(building.occupants) < building.capacity:
            building.occupants.append(entity_id)
            return True
        return False

    @staticmethod
    def remove_occupant(building: BuildingComponent, entity_id: int) -> None:
        """移除 occupants"""
        if entity_id in building.occupants:
            building.occupants.remove(entity_id)

    @staticmethod
    def can_add(inventory: BuildingInventoryComponent) -> bool:
        """是否还能添加物品"""
        return len(inventory.items) < inventory.max_items

    @staticmethod
    def add_item(inventory: BuildingInventoryComponent, entity_id: int, amount: float = 1.0) -> bool:
        """添加物品"""
        if not BuildingSystem.can_add(inventory):
            return False
        inventory.items[entity_id] = inventory.items.get(entity_id, 0.0) + amount
        return True

    @staticmethod
    def remove_item(inventory: BuildingInventoryComponent, entity_id: int, amount: float = 1.0) -> float:
        """移除物品，返回实际移除数量"""
        current = inventory.items.get(entity_id, 0.0)
        removed = min(current, amount)
        if removed >= current:
            del inventory.items[entity_id]
        else:
            inventory.items[entity_id] = current - removed
        return removed
