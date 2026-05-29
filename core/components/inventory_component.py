#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:inventory_component.py
@说明:物品栏组件
@时间:2026/03/13 11:15:43
@作者:Sherry
@版本:1.0
'''

# 已从 human/components/economic/inventory/inventory_component.py 迁移至此
# 向后兼容导入: from human.components.economic.inventory.inventory_component import InventoryComponent
from dataclasses import dataclass, field
from core.component import Component
from core.entity import Entity
from core.world import World


@dataclass
class InventoryComponent(Component):
    """
    非堆叠库存（存 Entity 引用）

    Args:
        items: 持有的实体（例如 food_entity）
        capacity: 最大容量
    """
    capacity: int = 20
    items: list = field(default_factory=list)
    
    # -------------------------
    # 添加物品
    # -------------------------
    def add(self, entity) -> bool:
        if len(self.items) >= self.capacity:
            return False
        self.items.append(entity)
        return True

    # -------------------------
    # 移除物品
    # -------------------------
    def remove(self, entity) -> bool:
        if entity in self.items:
            self.items.remove(entity)
            return True
        return False

    # -------------------------
    # 查找某类物品
    # -------------------------
    def find(self, component_type: type, world: World) -> Entity | None:
        for e in self.items:
            if world.get_component(e, component_type) is not None:
                return e
        return None