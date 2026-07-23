#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArchetypeStore — v4.0 核心重构

职责：
    - Archetype-based 组件存储
    - 高效组件查询（无需集合交集）
    - 实体组件变更时自动迁移 Archetype

设计原则：
    - 参考 Bevy/Unity DOTS 的 Archetype 设计
    - 列式存储，内存局部性好
    - 查询时直接遍历匹配的 Archetype，O(n) 无额外开销

关键概念：
    - Archetype: 组件类型的唯一组合，如 (Health, Position)
    - Chunk: Archetype 内部的连续内存块（未来扩展）
"""

import logging
from typing import Dict, List, Tuple, Type, Iterator, Optional, Set
from collections import defaultdict, OrderedDict

from core.entity import Entity
from core.component import Component

logger = logging.getLogger(__name__)


def _get_entity_id(entity) -> int:
    """
    统一提取实体 ID，兼容 Entity 对象和 int 类型。
    
    Args:
        entity: Entity 实例或 int 类型的 entity_id
        
    Returns:
        int: 实体 ID
    """
    return entity.id if hasattr(entity, 'id') else entity


def _hash_types(component_types: Tuple[Type[Component], ...]) -> int:
    """为组件类型组合生成唯一哈希"""
    return hash(tuple(sorted(id(t) for t in component_types)))


def _is_subset(query_types: Tuple[Type[Component], ...], archetype_types: Tuple[Type[Component], ...]) -> bool:
    """检查 query_types 是否是 archetype_types 的子集"""
    query_set = set(query_types)
    arch_set = set(archetype_types)
    return query_set.issubset(arch_set)


from dataclasses import fields

class Archetype:
    """
    Archetype = 组件类型的唯一组合

    内部混合存储：
    - entities: List[int]         # 行：实体 ID 列表
    - columns: Dict[Type, List[Component]]   # 兼容旧API的组件对象数组（AoS）
    - fields: Dict[Type[Component], Dict[str, List]]   # SoA字段数组（高性能访问用）
    """

    def __init__(self, component_types: Tuple[Type[Component], ...]):
        self.id = _hash_types(component_types)
        self.component_types = component_types
        self.entities: List[int] = []
        self.columns: Dict[Type[Component], List[Component]] = {
            t: [] for t in component_types
        }
        self.entity_index: Dict[int, int] = {}  # entity_id -> row_index

        # SoA存储：每个组件的每个字段对应一个连续数组（高性能访问用）
        self.fields: Dict[Type[Component], Dict[str, List]] = {}
        for comp_type in component_types:
            self.fields[comp_type] = {}
            for f in fields(comp_type):
                self.fields[comp_type][f.name] = []

    def add_entity(self, entity, components: Dict[Type[Component], Component]):
        """添加实体及其组件到 Archetype"""
        row_idx = len(self.entities)
        self.entities.append(entity)
        entity_id = _get_entity_id(entity)
        self.entity_index[entity_id] = row_idx

        for comp_type in self.component_types:
            comp = components.get(comp_type)
            if comp is None:
                raise ValueError(f"缺少组件 {comp_type.__name__}")
            # 更新AoS列（兼容旧API）
            self.columns[comp_type].append(comp)
            # 更新SoA字段数组（高性能用）
            for f in fields(comp_type):
                self.fields[comp_type][f.name].append(getattr(comp, f.name))

    def remove_entity(self, entity_id: int) -> Dict[Type[Component], Component]:
        """从 Archetype 移除实体，返回其组件"""
        row_idx = self.entity_index.get(entity_id)
        if row_idx is None:
            raise ValueError(f"实体 {entity_id} 不在此 Archetype 中")

        # 收集要移除的组件
        removed_components = {}
        for comp_type in self.component_types:
            removed_components[comp_type] = self.columns[comp_type][row_idx]

        # 用最后一个元素填补空缺（保持列表连续）
        last_idx = len(self.entities) - 1
        if row_idx != last_idx:
            last_entity = self.entities[last_idx]
            self.entities[row_idx] = last_entity
            self.entity_index[_get_entity_id(last_entity)] = row_idx

            # 移动AoS列
            for comp_type in self.component_types:
                self.columns[comp_type][row_idx] = self.columns[comp_type][last_idx]

            # 移动SoA字段数组
            for comp_type in self.component_types:
                for f_name in self.fields[comp_type]:
                    self.fields[comp_type][f_name][row_idx] = self.fields[comp_type][f_name][last_idx]

        # 移除最后一个元素
        self.entities.pop()
        for comp_type in self.component_types:
            self.columns[comp_type].pop()
            for f_name in self.fields[comp_type]:
                self.fields[comp_type][f_name].pop()

        del self.entity_index[entity_id]
        return removed_components

    def get_component(self, entity_id: int, component_type: Type[Component]) -> Optional[Component]:
        """获取实体的指定组件（兼容旧API）"""
        row_idx = self.entity_index.get(entity_id)
        if row_idx is None:
            return None
        return self.columns.get(component_type, [None])[row_idx] if row_idx < len(self.columns.get(component_type, [])) else None

    def get_field_array(self, component_type: Type[Component], field_name: str) -> Optional[List]:
        """获取指定组件的指定字段的连续数组（高性能API）"""
        comp_fields = self.fields.get(component_type)
        if comp_fields is None:
            return None
        return comp_fields.get(field_name)

    def has_component(self, entity_id: int, component_type: Type[Component]) -> bool:
        """检查指定实体是否拥有某类组件"""
        row_idx = self.entity_index.get(entity_id)
        if row_idx is None:
            return False
        return component_type in self.component_types

    def __len__(self) -> int:
        return len(self.entities)

    def __repr__(self):
        type_names = [t.__name__ for t in self.component_types]
        return f"<Archetype id={self.id} types={type_names} count={len(self)}>"


class ArchetypeStore:
    """
    Archetype 存储管理器

    管理所有 Archetype，处理实体组件的添加、移除、查询。
    """

    def __init__(self):
        # archetype_id -> Archetype
        self._archetypes: Dict[int, Archetype] = {}

        # entity_id -> archetype_id
        self._entity_archetype: Dict[int, int] = {}

        # 查询缓存: LRU缓存，最多保存最近1000条查询结果
        self._query_cache: OrderedDict[Tuple[Type[Component], ...], List[Tuple[Entity, ...]]] = OrderedDict()
        self._query_cache_max_size = 1000

        # 统计
        self._stats = {
            "archetype_count": 0,
            "entity_count": 0,
            "query_count": 0,
            "cache_hit": 0,
            "cache_miss": 0,
        }

    # === 组件管理 ===

    def add_component(self, entity, component: Component):
        """
        为实体添加组件

        实体会从当前 Archetype 迁移到新的 Archetype。
        """
        comp_type = type(component)
        entity_id = _get_entity_id(entity)

        # 获取当前 Archetype
        old_arch_id = self._entity_archetype.get(entity_id)

        # 计算新 Archetype 的类型签名
        if old_arch_id is not None:
            old_arch = self._archetypes[old_arch_id]
            # 如果已存在该组件类型，先移除旧组件
            if comp_type in old_arch.component_types:
                self.remove_component(entity, comp_type)
                old_arch_id = self._entity_archetype.get(entity_id)
                old_arch = self._archetypes.get(old_arch_id) if old_arch_id else None

            new_types = tuple(sorted(set(old_arch.component_types + (comp_type,)), key=lambda t: id(t)))
        else:
            new_types = (comp_type,)

        new_arch_id = _hash_types(new_types)

        # 创建或获取新 Archetype
        if new_arch_id not in self._archetypes:
            self._archetypes[new_arch_id] = Archetype(new_types)
            self._stats["archetype_count"] += 1

        new_arch = self._archetypes[new_arch_id]

        # 迁移实体数据
        self._migrate_entity(entity, old_arch_id, new_arch_id, component)

        # 使查询缓存精确失效（只清除包含新组件类型的查询）
        self._invalidate_cache([comp_type])

    def remove_component(self, entity, component_type: Type[Component]):
        """
        从实体移除组件

        实体会从当前 Archetype 迁移到新的 Archetype。
        """
        # 兼容：entity 可能是 int（entity_id）
        entity_id = _get_entity_id(entity)
        old_arch_id = self._entity_archetype.get(entity_id)

        if old_arch_id is None:
            return

        old_arch = self._archetypes[old_arch_id]

        if component_type not in old_arch.component_types:
            return

        # 计算新 Archetype 的类型签名
        new_types = tuple(sorted(
            [t for t in old_arch.component_types if t != component_type],
            key=lambda t: id(t)
        ))

        if not new_types:
            # 实体没有任何组件了，从存储中移除
            old_arch.remove_entity(entity_id)
            del self._entity_archetype[entity_id]
            self._stats["entity_count"] -= 1
            self._invalidate_cache()  # 实体被移除，全量失效
            return

        new_arch_id = _hash_types(new_types)

        # 创建或获取新 Archetype
        if new_arch_id not in self._archetypes:
            self._archetypes[new_arch_id] = Archetype(new_types)
            self._stats["archetype_count"] += 1

        # 迁移实体（不添加新组件）
        self._migrate_entity(entity, old_arch_id, new_arch_id, None)
        self._invalidate_cache([component_type])

    def _migrate_entity(self, entity, old_arch_id: Optional[int],
                        new_arch_id: int, new_component: Optional[Component]):
        """将实体从旧 Archetype 迁移到新 Archetype"""
        entity_id = _get_entity_id(entity)
        components: Dict[Type[Component], Component] = {}

        # 从旧 Archetype 收集组件
        if old_arch_id is not None and old_arch_id in self._archetypes:
            old_arch = self._archetypes[old_arch_id]
            removed = old_arch.remove_entity(entity_id)
            components.update(removed)

            # 清理空 Archetype
            if len(old_arch) == 0:
                del self._archetypes[old_arch_id]
                self._stats["archetype_count"] -= 1

        # 添加新组件
        if new_component is not None:
            components[type(new_component)] = new_component

        # 添加到新 Archetype
        new_arch = self._archetypes[new_arch_id]
        new_arch.add_entity(entity_id, components)
        self._entity_archetype[entity_id] = new_arch_id

        if old_arch_id is None:
            self._stats["entity_count"] += 1

    # === 查询 ===

    def get_component(self, entity, component_type: Type[Component]) -> Optional[Component]:
        """获取实体的指定组件"""
        entity_id = _get_entity_id(entity)
        arch_id = self._entity_archetype.get(entity_id)
        if arch_id is None:
            return None

        arch = self._archetypes[arch_id]
        return arch.get_component(entity_id, component_type)

    def has_component(self, entity, component_type: Type[Component]) -> bool:
        """检查实体是否有指定组件"""
        entity_id = _get_entity_id(entity)
        arch_id = self._entity_archetype.get(entity_id)
        if arch_id is None:
            return False

        arch = self._archetypes[arch_id]
        return arch.has_component(entity_id, component_type)

    def get_entity_components(self, entity) -> Dict[Type[Component], Component]:
        """获取实体的所有组件"""
        entity_id = _get_entity_id(entity)
        arch_id = self._entity_archetype.get(entity_id)
        if arch_id is None:
            return {}

        arch = self._archetypes[arch_id]
        return {
            comp_type: arch.get_component(entity_id, comp_type)
            for comp_type in arch.component_types
        }

    def get_all_components_by_type(self) -> Dict[Type[Component], Dict[int, Component]]:
        """获取所有组件，按类型分组 {comp_type: {entity_id: component}}"""
        result: Dict[Type[Component], Dict[int, Component]] = {}
        for archetype in self._archetypes.values():
            for i, entity in enumerate(archetype.entities):
                entity_id = _get_entity_id(entity)
                for comp_type, column in archetype.columns.items():
                    if comp_type not in result:
                        result[comp_type] = {}
                    result[comp_type][entity_id] = column[i]
        return result

    def query_entities(self, component_types: tuple) -> list:
        """查询具有指定组件组合的实体ID列表"""
        result = []
        for archetype in list(self._archetypes.values()):
            if _is_subset(component_types, archetype.component_types):
                for entity in archetype.entities:
                    entity_id = _get_entity_id(entity)
                    result.append(entity_id)
        return result

    def query(self, *component_types: Type[Component]) -> Iterator[Tuple[int, list]]:
        """
        查询具有指定组件组合的实体

        直接遍历匹配的 Archetype，无需集合交集计算。
        返回 (entity_id, [comp1, comp2, ...]) 元组。
        """
        cache_key = component_types

        # 尝试从缓存获取
        if cache_key in self._query_cache:
            self._stats["cache_hit"] += 1
            # LRU: 命中时移到末尾表示最近使用
            self._query_cache.move_to_end(cache_key)
            yield from self._query_cache[cache_key]
            return

        self._stats["cache_miss"] += 1
        self._stats["query_count"] += 1

        # 执行查询（复制键列表避免迭代时修改）
        result = []
        for archetype in list(self._archetypes.values()):
            if _is_subset(component_types, archetype.component_types):
                # 直接遍历连续内存
                for i, entity in enumerate(archetype.entities):
                    # v3.9 兼容：返回 (entity, [comp1, comp2, ...])
                    comps = [archetype.columns[t][i] for t in component_types]
                    item = (entity, comps)
                    result.append(item)
                    yield item

        # 缓存结果
        self._query_cache[cache_key] = result
        # LRU: 超过容量弹出最少使用的（最前面的）
        if len(self._query_cache) > self._query_cache_max_size:
            self._query_cache.popitem(last=False)

    def query_one(self, component_type: Type[Component]) -> Optional[Tuple[int, Component]]:
        """查询单个组件，返回第一个匹配结果 (entity_id, component)"""
        try:
            return next(self.query(component_type))
        except StopIteration:
            return None

    # === 实体生命周期 ===

    def remove_entity(self, entity):
        """移除实体及其所有组件"""
        entity_id = _get_entity_id(entity)
        arch_id = self._entity_archetype.get(entity_id)

        if arch_id is None:
            return

        arch = self._archetypes[arch_id]
        components = arch.remove_entity(entity_id)
        del self._entity_archetype[entity_id]
        self._stats["entity_count"] -= 1

        # 回收所有组件到对象池
        from core.component_pool import component_pool
        for comp in components.values():
            component_pool.recycle(comp)

        # 清理空 Archetype
        if len(arch) == 0:
            del self._archetypes[arch_id]
            self._stats["archetype_count"] -= 1

        self._invalidate_cache()  # 实体被移除，全量失效

    # === 缓存管理 ===

    def _invalidate_cache(self, affected_component_types=None):
        """使查询缓存精确失效
        
        Args:
            affected_component_types: 受影响的组件类型列表。为 None 时全量清除。
        """
        if affected_component_types is None:
            self._query_cache.clear()
            return
        
        affected_set = set(affected_component_types)
        keys_to_remove = [k for k in self._query_cache.keys() 
                         if any(t in affected_set for t in k)]
        for k in keys_to_remove:
            del self._query_cache[k]

    def clear_cache(self):
        """手动清空查询缓存"""
        self._query_cache.clear()

    # === 统计 ===

    def get_stats(self) -> dict:
        """获取统计信息"""
        total_cache = self._stats["cache_hit"] + self._stats["cache_miss"]
        hit_rate = self._stats["cache_hit"] / total_cache if total_cache > 0 else 0.0

        return {
            "archetype_count": self._stats["archetype_count"],
            "entity_count": self._stats["entity_count"],
            "query_count": self._stats["query_count"],
            "cache_hit": self._stats["cache_hit"],
            "cache_miss": self._stats["cache_miss"],
            "cache_hit_rate": hit_rate,
        }

    def get_archetype_info(self) -> List[dict]:
        """获取所有 Archetype 的信息"""
        return [
            {
                "id": arch.id,
                "types": [t.__name__ for t in arch.component_types],
                "entity_count": len(arch),
            }
            for arch in self._archetypes.values()
        ]

    # === 调试 ===

    def __repr__(self):
        return f"<ArchetypeStore archetypes={self._stats['archetype_count']} entities={self._stats['entity_count']}>"