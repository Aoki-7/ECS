#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EntityManager — v4.0 核心重构

职责：
    - Entity ID 分配、回收、生命周期管理
    - 与 EntityPool 集成
    - 独立于 World 的专职管理器

设计原则：
    - 单一职责：只管理 Entity，不处理 Component
    - 向后兼容：保持与 v3.9 Entity.create()/destroy() 兼容
"""

import logging
from typing import Optional, Dict, Set

from core.entity import Entity

logger = logging.getLogger(__name__)


class EntityManager:
    """
    实体管理器

    管理所有实体的生命周期，包括：
    - 创建新实体（支持对象池）
    - 销毁实体（回收 ID）
    - 实体存在性查询
    - 实体元数据管理
    """

    def __init__(self):
        # id -> Entity
        self._entities: Dict[int, Entity] = {}

        # 已销毁的实体 ID（用于存在性检查）
        self._destroyed_ids: Set[int] = set()

        # 统计
        self._stats = {
            "created": 0,
            "destroyed": 0,
            "active": 0,
        }

    # === 创建 ===

    def create(self) -> Entity:
        """
        创建新实体

        直接使用 Entity.create()，由 Entity 类内部处理对象池。
        """
        entity = Entity.create()
        self._entities[entity.id] = entity
        self._stats["created"] += 1
        self._stats["active"] += 1
        return entity

    # === 销毁 ===

    def destroy(self, entity: Entity) -> bool:
        """
        销毁实体

        Args:
            entity: 要销毁的实体

        Returns:
            bool: 是否成功销毁
        """
        if not self.has_entity(entity):
            return False

        entity_id = entity.id

        # 从管理器中移除
        del self._entities[entity_id]
        self._destroyed_ids.add(entity_id)

        # 回收实体 ID（由 Entity.destroy 内部处理对象池）
        Entity.destroy(entity)

        self._stats["destroyed"] += 1
        self._stats["active"] -= 1
        return True

    # === 查询 ===

    def has_entity(self, entity: Entity) -> bool:
        """检查实体是否存在且未过期"""
        current = self._entities.get(entity.id)
        return (
            current is not None
            and current.generation == entity.generation
        )

    def get_entity(self, entity_id: int) -> Optional[Entity]:
        """根据 ID 获取实体"""
        return self._entities.get(entity_id)

    def get(self, entity_id: int) -> Optional[Entity]:
        """get_entity alias for v3.x compatibility"""
        return self.get_entity(entity_id)

    def get_all_entities(self) -> Dict[int, Entity]:
        """获取所有活跃实体"""
        return self._entities.copy()

    def get_active_count(self) -> int:
        """获取活跃实体数量"""
        return len(self._entities)

    # === 统计 ===

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "created": self._stats["created"],
            "destroyed": self._stats["destroyed"],
            "active": self._stats["active"],
        }

    def reset(self):
        """重置管理器（主要用于测试）"""
        self._entities.clear()
        self._destroyed_ids.clear()
        self._stats = {
            "created": 0,
            "destroyed": 0,
            "active": 0,
        }

    # === 迭代支持 ===

    def __iter__(self):
        """迭代所有活跃实体"""
        return iter(self._entities.values())

    def __len__(self) -> int:
        """活跃实体数量"""
        return len(self._entities)

    def count(self) -> int:
        """活跃实体数量（兼容方法）"""
        return len(self._entities)

    def __contains__(self, entity: Entity) -> bool:
        """检查实体是否存在"""
        return self.has_entity(entity)
