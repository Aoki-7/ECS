#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECS Query API — v3.7 核心重构

提供声明式查询接口，隐藏 World 内部实现细节：
  world.query(HealthComponent, PositionComponent)

设计原则：
  - 只读查询：返回 (Entity, *components) 元组
  - 缓存友好：同一 tick 内相同查询复用结果
  - 类型安全：支持类型注解和 IDE 自动补全
"""

from typing import TypeVar, Type, Iterator, Tuple, Any
from core.world import World
from core.entity import Entity
from core.component import Component

C = TypeVar('C', bound=Component)


class QueryResult:
    """
    查询结果包装器

    支持迭代和解包：
        for entity, health, pos in world.query(HealthComponent, PositionComponent):
            ...
    """

    def __init__(self, world: World, component_types: Tuple[Type[Component], ...]):
        self._world = world
        self._component_types = component_types
        self._cache_key = component_types
        self._cached = False
        self._result = []

    def __iter__(self) -> Iterator[Tuple[Entity, ...]]:
        """惰性执行查询，支持缓存"""
        # 尝试从 World 查询缓存获取
        if self._cache_key in self._world._query_cache:
            for item in self._world._query_cache[self._cache_key]:
                # 统一缓存格式为 (Entity, [components])，对外解包
                if len(item) == 2 and isinstance(item[1], list):
                    entity, comps = item
                    yield (entity, *comps)
                else:
                    yield item
            return

        # 执行查询
        result = []
        for entity, components in self._world.get_components(*self._component_types):
            # 缓存统一保存为 (Entity, [components])，便于与 get_components 共享
            item = (entity, components)
            result.append(item)
            yield (entity, *components)

        # 缓存结果
        self._world._query_cache[self._cache_key] = result

    def first(self) -> Tuple[Entity, ...] | None:
        """获取第一个结果"""
        try:
            return next(iter(self))
        except StopIteration:
            return None

    def count(self) -> int:
        """获取结果数量"""
        return sum(1 for _ in self)

    def to_list(self) -> list:
        """转换为列表（消耗迭代器）"""
        return list(self)


class WorldQueryMixin:
    """
    World 查询混入类

    通过 monkey-patch 或继承添加到 World 类：
        World.__bases__ = World.__bases__ + (WorldQueryMixin,)
    """

    def query(self, *component_types: Type[C]) -> QueryResult:
        """
        声明式查询接口

        用法：
            # 查询单个组件
            for entity, health in world.query(HealthComponent):
                ...

            # 查询多个组件
            for entity, health, pos in world.query(HealthComponent, PositionComponent):
                ...

            # 获取第一个结果
            result = world.query(HealthComponent).first()
            if result:
                entity, health = result

            # 获取数量
            count = world.query(HealthComponent).count()
        """
        return QueryResult(self, component_types)

    def query_one(self, component_type: Type[C]) -> Tuple[Entity, C] | None:
        """
        查询单个组件的快捷方法

        用法：
            result = world.query_one(HealthComponent)
            if result:
                entity, health = result
        """
        result = self.query(component_type).first()
        return result


# 将查询 API 方法直接注入 World 类
World.query = WorldQueryMixin.query
World.query_one = WorldQueryMixin.query_one