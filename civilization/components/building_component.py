#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建筑组件

v3.0.1 新增 — 建筑实体化
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from core.component import Component


@dataclass(slots=True)
class BuildingComponent(Component):
    """
    建筑组件

    定义建筑的基本属性。
    """
    building_type: str = "hut"  # hut, workshop, storage, farm
    owner_id: int = -1  # 建造者/所有者 ID
    durability: float = 100.0  # 耐久度
    max_durability: float = 100.0
    capacity: int = 0  # 容量（存储建筑用）
    occupants: List[int] = field(default_factory=list)  # 当前 occupants
    is_active: bool = True  # 是否可用

    def take_damage(self, damage: float) -> None:
        """受到损伤"""
        self.durability = max(0.0, self.durability - damage)
        if self.durability <= 0:
            self.is_active = False

    def repair(self, amount: float) -> None:
        """修复建筑"""
        self.durability = min(self.max_durability, self.durability + amount)
        if self.durability > 0:
            self.is_active = True

    def add_occupant(self, entity_id: int) -> bool:
        """添加 occupants"""
        if len(self.occupants) < self.capacity:
            self.occupants.append(entity_id)
            return True
        return False

    def remove_occupant(self, entity_id: int) -> None:
        """移除 occupants"""
        if entity_id in self.occupants:
            self.occupants.remove(entity_id)


@dataclass(slots=True)
class BuildingInventoryComponent(Component):
    """
    建筑库存组件

    存储建筑内的物品。
    """
    items: Dict[int, float] = field(default_factory=dict)  # entity_id -> amount
    max_items: int = 20

    def can_add(self) -> bool:
        """是否还能添加物品"""
        return len(self.items) < self.max_items

    def add_item(self, entity_id: int, amount: float = 1.0) -> bool:
        """添加物品"""
        if not self.can_add():
            return False
        self.items[entity_id] = self.items.get(entity_id, 0.0) + amount
        return True

    def remove_item(self, entity_id: int, amount: float = 1.0) -> float:
        """移除物品，返回实际移除数量"""
        current = self.items.get(entity_id, 0.0)
        removed = min(current, amount)
        if removed >= current:
            del self.items[entity_id]
        else:
            self.items[entity_id] = current - removed
        return removed
