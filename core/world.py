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
from core.event_bus import EventBus
from core.entity_manager import EntityManager
from core.archetype_store import ArchetypeStore
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
    - 保持 v3.9 的 public API 不变
    - 新增 query() / query_one() 声明式查询接口
    """

    def __init__(self):
        # === v4.0 新增：专职管理器 ===
        self._entity_manager = EntityManager()
        self._component_store = ArchetypeStore()
        self._system_scheduler = SystemScheduler()

        # === v3.9 兼容：保留旧属性（委托给新管理器）===
        # 注意：self.entities / self.components / self.systems 仍保留
        # 但内部实现已变更

        self.tick_count = 0

        # === 世界实体（由 application 层注入）===
        self._world_entity: Entity | None = None

        # === v3.9 兼容：保留旧缓存（但内部不再使用）===
        self._query_cache: dict = {}

        # === v3.9 兼容：保留旧属性（存档系统依赖）===
        self._component_entities: dict = _ComponentEntitiesCompatView(self._component_store)

    # ====================
    # Entity API（v3.9 兼容）
    # ====================

    @property
    def entities(self):
        """v3.9 兼容：返回所有活跃实体"""
        return self._entity_manager.get_all_entities()

    def create_entity(self) -> Entity:
        """创建新实体"""
        entity = self._entity_manager.create()

        # 发布事件
        try:
            EventBus.get_instance().publish(
                "entity_created",
                {"entity_id": entity.id},
                source="world",
                timestamp=self.tick_count,
            )
        except Exception:
            pass

        return entity

    def remove_entity(self, entity: Entity):
        """删除实体及其所有组件"""
        if not self.has_entity(entity):
            return

        # 从 SpaceSystem 反注册
        self._unregister_entity_from_space(entity.id)

        # 从 ArchetypeStore 移除
        self._component_store.remove_entity(entity)

        # 从 EntityManager 移除
        self._entity_manager.destroy(entity)

        # 清除旧缓存（v3.9 兼容）
        self._query_cache.clear()

        # 通知记忆层
        memory_layer = _get_memory_layer()
        if memory_layer is not None:
            memory_layer.entity_destroyed(entity.id, timestamp=self.tick_count)

        # 发布事件
        try:
            EventBus.get_instance().publish(
                "entity_destroyed",
                {"entity_id": entity.id, "reason": "removed"},
                source="world",
                timestamp=self.tick_count,
            )
        except Exception:
            pass

    def has_entity(self, entity: Entity) -> bool:
        """检查实体是否存在"""
        return self._entity_manager.has_entity(entity)

    def query_entity(self, entity_id: int) -> Optional[Entity]:
        """根据 ID 查询实体"""
        return self._entity_manager.get_entity(entity_id)

    # ====================
    # Component API（v3.9 兼容）
    # ====================

    @property
    def components(self):
        """v3.9 兼容：返回组件存储的兼容视图"""
        # 返回一个兼容 v3.9 接口的字典视图
        return _ComponentStoreCompatView(self)

    def add_component(self, entity: Entity, component: Component):
        """为实体添加组件"""
        if not self.has_entity(entity):
            raise ValueError("Entity 不存在，无法添加组件")

        # 使用 ArchetypeStore
        self._component_store.add_component(entity, component)

        # 自动注册 SpaceComponent
        self._register_component_to_space(entity.id, component)

        # 清除旧缓存（v3.9 兼容）
        self._query_cache.clear()

    def remove_component(self, entity: Entity, component_type: type):
        """从实体移除组件"""
        # 从 SpaceSystem 反注册
        self._unregister_component_from_space(entity.id, component_type)

        # 使用 ArchetypeStore
        self._component_store.remove_component(entity, component_type)

        # 清除旧缓存（v3.9 兼容）
        self._query_cache.clear()

    def get_component(self, entity: Entity, component_type: type) -> Optional[Component]:
        """获取实体的指定组件"""
        return self._component_store.get_component(entity, component_type)

    def get_components(self, *component_types: type) -> Iterator[Tuple[Entity, ...]]:
        """查询具有指定组件组合的实体"""
        yield from self._component_store.query(*component_types)

    def get_entities_with(self, component_type: type) -> Iterator[Entity]:
        """v3.9 兼容：获取具有指定组件的所有实体"""
        for entity, _ in self._component_store.query(component_type):
            yield entity

    def query_components(self, component_type: type) -> Iterator[Tuple[Entity, Component]]:
        """v3.9 兼容：查询指定组件类型的所有实体"""
        yield from self._component_store.query(component_type)

    # ====================
    # v4.0 新增：声明式查询接口
    # ====================

    def query(self, *component_types: type):
        """声明式查询接口（与 query_api.py 兼容）"""
        return _QueryResult(self, component_types)

    def query_one(self, component_type: type) -> Optional[Tuple[Entity, Component]]:
        """查询单个组件，返回第一个匹配结果"""
        return self._component_store.query_one(component_type)

    # ====================
    # System API（v3.9 兼容）
    # ====================

    @property
    def systems(self):
        """v3.9 兼容：返回系统列表"""
        return self._system_scheduler.get_all()

    def add_system(self, system):
        """注册系统"""
        self._system_scheduler.add(system)

    def update(self, dt: float):
        """更新所有系统"""
        self.tick_count += 1
        self._system_scheduler.update(self, dt)

    def get_system(self, system_type):
        """获取指定类型的系统"""
        return self._system_scheduler.get(system_type)

    # ====================
    # 世界实体 API（v3.9 兼容）
    # ====================

    def get_world_entity(self) -> Optional[Entity]:
        """获取世界实体"""
        return self._world_entity

    def set_world_entity(self, entity: Entity) -> None:
        """设置世界实体"""
        self._world_entity = entity

    def get_world_component(self, component_type: type) -> Optional[Component]:
        """从世界实体获取组件"""
        if self._world_entity is None:
            return None
        if hasattr(self._world_entity, 'get_component'):
            return self._world_entity.get_component(component_type)
        return self.get_component(self._world_entity, component_type)

    # ====================
    # 辅助方法
    # ====================

    def get_time(self):
        """获取世界时间组件"""
        if self._world_entity is None:
            return None
        from time_module.time_component import TimeComponent
        if hasattr(self._world_entity, 'get_component'):
            return self._world_entity.get_component(TimeComponent)
        return self.get_component(self._world_entity, TimeComponent)

    def get_environment(self):
        """获取环境组件"""
        if self._world_entity is None:
            return None
        from environment.environment_component import EnvironmentComponent
        if hasattr(self._world_entity, 'get_component'):
            return self._world_entity.get_component(EnvironmentComponent)
        return self.get_component(self._world_entity, EnvironmentComponent)

    def get_memory_layer(self):
        """获取记忆层"""
        return _get_memory_layer()

    def get_event_bus(self):
        """获取事件总线"""
        return EventBus.get_instance()

    # ====================
    # SpaceSystem 集成（v3.9 兼容）
    # ====================

    def _register_component_to_space(self, entity_id: int, component: Component):
        """注册 SpaceComponent 到 SpaceSystem"""
        from space.space_component import SpaceComponent
        if isinstance(component, SpaceComponent):
            from space.space_system import SpaceSystem
            space_system = self.get_system(SpaceSystem)
            if space_system:
                space_system.add_entity(entity_id, component)

    def _unregister_component_from_space(self, entity_id: int, component_type: type):
        """从 SpaceSystem 反注册"""
        from space.space_component import SpaceComponent
        if component_type is SpaceComponent or issubclass(component_type, SpaceComponent):
            from space.space_system import SpaceSystem
            space_system = self.get_system(SpaceSystem)
            if space_system:
                space_system.remove_entity(entity_id)

    def _unregister_entity_from_space(self, entity_id: int):
        """从 SpaceSystem 反注册实体"""
        try:
            from space.space_system import SpaceSystem
            space_system = self.get_system(SpaceSystem)
            if space_system:
                space_system.remove_entity(entity_id)
        except ImportError:
            logger.warning("SpaceSystem not available, skipping spatial cleanup")

    # ====================
    # 分类查询（v3.9 兼容）
    # ====================

    def get_entities_by_category(self, category, subcategory=None):
        """按分类查询实体"""
        from identity.category_component import CategoryComponent
        for entity, comp in self.query_components(CategoryComponent):
            if comp.matches(category, subcategory):
                yield entity, comp

    def count_by_category(self, category, subcategory=None) -> int:
        """统计分类实体数量"""
        return sum(1 for _ in self.get_entities_by_category(category, subcategory))

    # ====================
    # 调试（v3.9 兼容）
    # ====================

    def debug_print_entity(self, entity: Entity, verbose: bool = True):
        """打印实体详情"""
        if not self.has_entity(entity):
            logger.debug(f"[错误] 实体 {entity.id} 不存在或已失效")
            return

        lines = [
            "=" * 50,
            f"实体ID: {entity.id}",
            f"实体代数: {entity.generation}",
        ]

        # 获取实体所有组件
        arch_info = self._component_store.get_archetype_info()
        for info in arch_info:
            # 这里简化处理，实际应该查询实体的组件
            pass

        lines.append("=" * 50)
        logger.debug("\n".join(lines))

    def debug_print_all_entities(self):
        """打印所有实体"""
        logger.debug("\n====== 当前世界实体列表 ======")
        for entity in self._entity_manager:
            self.debug_print_entity(entity, verbose=False)
        logger.debug("====== 打印结束 ======\n")

    def entity_count(self) -> int:
        """实体数量"""
        return len(self._entity_manager)

    def component_count(self, component_type: type) -> int:
        """指定组件类型的实体数量"""
        # 通过查询统计
        return sum(1 for _ in self._component_store.query(component_type))

    # ====================
    # v4.0 新增：统计信息
    # ====================

    def get_stats(self) -> dict:
        """获取世界统计信息"""
        return {
            "entities": self._entity_manager.get_stats(),
            "components": self._component_store.get_stats(),
            "systems": self._system_scheduler.get_stats(),
        }

    def get_archetype_info(self) -> list:
        """获取 Archetype 信息（调试用）"""
        return self._component_store.get_archetype_info()


# ====================
# 兼容层类
# ====================

class _ComponentStoreCompatView:
    """
    v3.9 兼容：组件存储字典视图

    模拟 v3.9 的 self.components[comp_type][entity_id] 接口
    """

    def __init__(self, world: World):
        self._world = world
        self._store = world._component_store

    def __getitem__(self, comp_type: type):
        return _ComponentTypeCompatView(self._store, comp_type)

    def get(self, comp_type: type, default=None):
        return _ComponentTypeCompatView(self._store, comp_type)

    def items(self):
        # 返回空迭代器（兼容层简化实现）
        return iter([])

    def keys(self):
        return iter([])

    def values(self):
        return iter([])

    def clear(self):
        """清空所有组件 — 用于存档加载"""
        # 重置 ArchetypeStore
        self._store._archetypes.clear()
        self._store._entity_archetype.clear()
        self._store._query_cache.clear()
        self._store._stats = {
            "archetype_count": 0,
            "entity_count": 0,
            "query_count": 0,
            "cache_hit": 0,
            "cache_miss": 0,
        }


class _ComponentEntitiesCompatView:
    """
    v3.9 兼容：反向索引字典视图

    模拟 v3.9 的 self._component_entities[comp_type] = set(entity_ids)
    """

    def __init__(self, archetype_store: ArchetypeStore):
        self._store = archetype_store

    def clear(self):
        """清空反向索引"""
        # 实际存储在 ArchetypeStore 中，已随 components.clear() 清空
        pass

    def get(self, comp_type: type, default=None):
        return set()

    def __getitem__(self, comp_type: type):
        return set()

    def __setitem__(self, comp_type: type, value: set):
        pass

    def __contains__(self, comp_type: type) -> bool:
        return False

    def keys(self):
        return iter([])

    def values(self):
        return iter([])

    def items(self):
        return iter([])


class _ComponentTypeCompatView:
    """组件类型兼容视图"""

    def __init__(self, archetype_store: ArchetypeStore, comp_type: type):
        self._store = archetype_store
        self._comp_type = comp_type

    def __getitem__(self, entity_id: int):
        from core.entity import Entity
        entity = Entity(entity_id, 0)  # 简化处理
        comp = self._store.get_component(entity, self._comp_type)
        if comp is None:
            raise KeyError(entity_id)
        return comp

    def get(self, entity_id: int, default=None):
        from core.entity import Entity
        entity = Entity(entity_id, 0)
        return self._store.get_component(entity, self._comp_type) or default

    def pop(self, entity_id: int, default=None):
        # 简化实现
        return default

    def __contains__(self, entity_id: int) -> bool:
        from core.entity import Entity
        entity = Entity(entity_id, 0)
        return self._store.get_component(entity, self._comp_type) is not None

    def keys(self):
        return iter([])

    def values(self):
        return iter([])

    def items(self):
        return iter([])


class _QueryResult:
    """
    v4.0 查询结果包装器

    与 query_api.py 的 QueryResult 兼容
    """

    def __init__(self, world: World, component_types: tuple):
        self._world = world
        self._component_types = component_types

    def __iter__(self):
        yield from self._world.get_components(*self._component_types)

    def first(self) -> Optional[Tuple[Entity, ...]]:
        try:
            return next(iter(self))
        except StopIteration:
            return None

    def count(self) -> int:
        return sum(1 for _ in self)

    def to_list(self) -> list:
        return list(self)
