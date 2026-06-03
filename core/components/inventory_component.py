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


@dataclass(slots=True)
class InventoryComponent(Component):
    """
    非堆叠库存（存 entity_id，避免对已删除实体的对象引用泄漏）

    Args:
        items: 持有的实体 ID 列表（例如 food_entity.id）
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
        entity_id = entity.id if hasattr(entity, 'id') else entity
        self.items.append(entity_id)
        return True

    # -------------------------
    # 移除物品
    # -------------------------
    def remove(self, entity) -> bool:
        entity_id = entity.id if hasattr(entity, 'id') else entity
        if entity_id in self.items:
            self.items.remove(entity_id)
            return True
        return False

    # -------------------------
    # 查找某类物品
    # -------------------------
    def find(self, component_type: type, world: World):
        for entity_id in self.items:
            entity = world.query_entity(entity_id)
            if entity is not None and world.get_component(entity, component_type) is not None:
                return entity
        return None