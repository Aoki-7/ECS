#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
World — v4.0 核心重构

职责：
    - 协调者模式：委托职责给专职管理器
    - 生命周期管理：Entity / Component / System 的协调
    - 向后兼容：保持 v3.9 API 不变

设计原则：
    - World 不再直接存储数据，委托给 EntityManager / ArchetypeStore / SystemScheduler
    - 保留 v3.9 的 public API，内部实现替换为新架构
    - 事件总线保持全局单例（v4.1 再迁移到 per-World）
"""

import logging
import traceback
from typing import Optional, Iterator, Tuple

from core.entity import Entity
from core.component import Component
from core.world_event_bus import WorldEventBus
from core.entity_manager import EntityManager
from core.archetype_store import ArchetypeStore, _get_entity_id
from core.system_scheduler import SystemScheduler

logger = logging.getLogger(__name__)

# 记忆层导入（可选，延迟初始化以避免循环依赖）
_memory_layer = None

def _get_memory_layer():
    global _memory_layer
    if _memory_layer is None:
        try:
            from memory_layer import MemoryLayer
            _memory_layer = MemoryLayer.get_instance()
        except ImportError:
            _memory_layer = None
    return _memory_layer


class World:
    """
    ECS World — 协调者

    v4.0 变更：
    - 内部使用 EntityManager / ArchetypeStore / SystemScheduler
    - 使用 WorldEventBus 实现 per-World 事件隔离
    - 保持 v3.9 的 public API 不变
    """

    def __init__(self, world_id: str = "default"):
        # 核心管理器
        self._entity_manager = EntityManager()
        self._archetype_store = ArchetypeStore()
        self._system_scheduler = SystemScheduler()

        # 世界事件总线（per-World 事件隔离）
        self._event_bus = WorldEventBus(world_id)

        # 世界实体（存储全局组件如时间、环境配置）
        self._world_entity: Optional[Entity] = None

        # 时间
        self.tick_count = 0
        self._time = None  # TimeComponent 或兼容对象

        # 查询缓存（v3.9 兼容）
        self._query_cache = {}

        # 系统缓存（v3.9 兼容）
        self._system_cache = {}

        # 环境引用（v3.9 兼容）
        self._environment = None

        logger.info(f"[World] v4.0 World 初始化完成 (id={world_id})")

    # ====================
    # 事件总线
    # ====================

    @property
    def event_bus(self) -> WorldEventBus:
        """获取世界事件总线"""
        return self._event_bus

    def subscribe(self, event_type: str, handler, priority: int = 0, once: bool = False, filter_fn=None):
        """订阅世界事件"""
        return self._event_bus.subscribe(event_type, handler, priority, once, filter_fn)

    def unsubscribe(self, event_type: str, handler):
        """取消订阅世界事件"""
        self._event_bus.unsubscribe(event_type, handler)

    def publish(self, event_type: str, payload: dict, source: str = "world"):
        """发布世界事件"""
        self._event_bus.publish(event_type, payload, source=source, timestamp=self.tick_count)

    # ====================
    # 实体管理
    # ====================

    @property
    def entities(self):
        """v3.9 兼容：返回所有活跃实体"""
        return self._entity_manager.get_all_entities()

    def get_all_entities(self):
        """获取所有实体列表（兼容方法）"""
        return list(self._entity_manager.get_all_entities().values())

    def create_entity(self) -> Entity:
        """创建新实体"""
        entity = self._entity_manager.create()

        # 发布事件
        self._event_bus.publish("entity_created", {"entity_id": entity.id}, source="world")

        return entity

    def remove_entity(self, entity) -> None:
        """移除实体"""
        if entity is None:
            return

        entity_id = _get_entity_id(entity)
        
        # 先移除所有组件（触发组件移除事件）
        self._archetype_store.remove_entity(entity_id)

        # 再从实体管理器移除
        if hasattr(entity, 'id'):
            self._entity_manager.destroy(entity)
        else:
            # 如果传入的是 entity_id，需要先获取实体
            ent = self._entity_manager.get(entity_id)
            if ent:
                self._entity_manager.destroy(ent)

        # 发布事件
        self._event_bus.publish("entity_destroyed", {"entity_id": entity_id}, source="world")

    def query_entity(self, entity_id: int) -> Optional[Entity]:
        """根据 ID 查询实体"""
        return self._entity_manager.get(entity_id)

    def is_entity_alive(self, entity: Entity) -> bool:
        """检查实体是否存活"""
        return self._entity_manager.has_entity(entity)

    def has_entity(self, entity: Entity) -> bool:
        '''check whether entity exists in the world'''
        if entity is None:
            return False
        entity_id = _get_entity_id(entity)
        return self._entity_manager.get(entity_id) is not None

    # ====================
    # 组件管理
    # ====================

    def add_component(self, entity: Entity, component: Component) -> None:
        """为实体添加组件"""
        if entity is None or component is None:
            return
        
        entity_id = _get_entity_id(entity)
        self._archetype_store.add_component(entity_id, component)

        # 发布事件
        self._event_bus.publish(
            "component_added",
            {"entity_id": entity_id, "component_type": type(component).__name__},
            source="world"
        )

    def remove_component(self, entity: Entity, component_type: type) -> None:
        """从实体移除组件"""
        if entity is None:
            return
        
        entity_id = _get_entity_id(entity)
        self._archetype_store.remove_component(entity_id, component_type)

        # 发布事件
        self._event_bus.publish(
            "component_removed",
            {"entity_id": entity_id, "component_type": component_type.__name__},
            source="world"
        )

    def get_component(self, entity: Entity, component_type: type) -> Optional[Component]:
        """获取实体的组件"""
        if entity is None:
            return None
        
        entity_id = _get_entity_id(entity)
        return self._archetype_store.get_component(entity_id, component_type)

    def has_component(self, entity: Entity, component_type: type) -> bool:
        """检查实体是否有指定组件"""
        if entity is None:
            return False
        
        entity_id = _get_entity_id(entity)
        return self._archetype_store.has_component(entity_id, component_type)

    def get_components(self, *component_types) -> Iterator[Tuple[Entity, list]]:
        """查询具有指定组件组合的实体"""
        if not component_types:
            return

        # 使用 ArchetypeStore 查询
        entity_ids = self._archetype_store.query_entities(component_types)

        for entity_id in entity_ids:
            entity = self._entity_manager.get(entity_id)
            if entity is None:
                continue

            components = []
            for comp_type in component_types:
                comp = self._archetype_store.get_component(entity_id, comp_type)
                if comp is None:
                    break
                components.append(comp)
            else:
                # 所有组件都存在
                yield (entity, components)

    # ====================
    # 系统管理
    # ====================

    def add_system(self, system) -> None:
        """添加系统"""
        self._system_scheduler.add(system)
        if hasattr(system, 'on_add'):
            system.on_add(self)

    def remove_system(self, system_type: type) -> None:
        """移除系统"""
        system = self._system_scheduler.get(system_type)
        if system and hasattr(system, 'on_remove'):
            system.on_remove(self)
        self._system_scheduler.remove(system_type)

    def get_system(self, system_type: type):
        """获取系统实例"""
        return self._system_scheduler.get(system_type)

    def update(self, dt: float = 1.0) -> None:
        """更新所有系统"""
        self._system_scheduler.update(self, dt)
        self.tick_count += 1

    # ====================
    # 世界实体管理
    # ====================

    def get_world_entity(self) -> Optional[Entity]:
        """获取世界实体"""
        return self._world_entity

    def set_world_entity(self, entity: Entity) -> None:
        """设置世界实体"""
        self._world_entity = entity

    def get_world_component(self, component_type: type) -> Optional[Component]:
        """获取世界组件"""
        if self._world_entity is None:
            return None
        return self.get_component(self._world_entity, component_type)

    # ====================
    # 时间管理
    # ====================

    def get_time(self):
        """获取时间组件"""
        return self._time

    def set_time(self, time_component) -> None:
        """设置时间组件"""
        self._time = time_component

    # ====================
    # 环境管理
    # ====================

    def get_environment(self):
        """获取环境组件"""
        return self._environment

    def set_environment(self, environment) -> None:
        """设置环境组件"""
        self._environment = environment

    # ====================
    # 序列化
    # ====================

    def to_dict(self) -> dict:
        """序列化世界状态"""
        return {
            "tick_count": self.tick_count,
            "entity_count": self._entity_manager.count(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "World":
        """从字典恢复世界状态"""
        world = cls()
        world.tick_count = data.get("tick_count", 0)
        return world

    # ====================
    # 调试
    # ====================

    def __repr__(self) -> str:
        return f"<World entities={self._entity_manager.count()} systems={len(self._system_scheduler._systems)}>"
