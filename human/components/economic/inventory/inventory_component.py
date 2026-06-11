#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
物品栏组件

v3.9 迁移：从 core/components/ 移回 human/components/economic/inventory/
保持 core 层纯粹性。
"""

from dataclasses import dataclass, field
from core.component import Component
from core.world import World


@dataclass(slots=True)
class InventoryComponent(Component):
    """
    非堆叠库存（存 entity_id，避免对已删除实体的对象引用泄漏）
    """
    capacity: int = 20
    items: list = field(default_factory=list)

    def add(self, entity) -> bool:
        """添加物品"""
        if len(self.items) >= self.capacity:
            return False
        entity_id = entity.id if hasattr(entity, 'id') else entity
        self.items.append(entity_id)
        return True

    def remove(self, entity) -> bool:
        """移除物品"""
        entity_id = entity.id if hasattr(entity, 'id') else entity
        if entity_id in self.items:
            self.items.remove(entity_id)
            return True
        return False

    def find(self, component_type: type, world: World):
        """查找某类物品"""
        for entity_id in self.items:
            entity = world.query_entity(entity_id)
            if entity is not None and world.get_component(entity, component_type) is not None:
                return entity
        return None
