#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query API 测试
"""

import pytest
from dataclasses import dataclass

from core.world import World
from core.entity import Entity
from core.component import Component
from core.query_api import QueryResult, WorldQueryMixin


@dataclass
class HealthComponent(Component):
    current: float = 100.0
    max: float = 100.0


@dataclass
class PositionComponent(Component):
    x: float = 0.0
    y: float = 0.0


@dataclass
class VelocityComponent(Component):
    vx: float = 0.0
    vy: float = 0.0


class TestQueryAPI:
    """Query API 测试"""

    def test_query_single_component(self):
        """测试查询单个组件"""
        world = World()
        entity = world.create_entity()
        world.add_component(entity, HealthComponent(current=80.0))

        results = list(world.query(HealthComponent))
        assert len(results) == 1
        assert results[0][0].id == entity.id
        assert results[0][1].current == 80.0

    def test_query_multiple_components(self):
        """测试查询多个组件"""
        world = World()
        entity = world.create_entity()
        world.add_component(entity, HealthComponent(current=80.0))
        world.add_component(entity, PositionComponent(x=10.0, y=20.0))

        results = list(world.query(HealthComponent, PositionComponent))
        assert len(results) == 1
        assert results[0][0].id == entity.id
        assert results[0][1].current == 80.0
        assert results[0][2].x == 10.0

    def test_query_no_match(self):
        """测试无匹配结果"""
        world = World()
        entity = world.create_entity()
        world.add_component(entity, HealthComponent())

        results = list(world.query(VelocityComponent))
        assert len(results) == 0

    def test_query_first(self):
        """测试 first() 方法"""
        world = World()
        entity = world.create_entity()
        world.add_component(entity, HealthComponent(current=50.0))

        result = world.query(HealthComponent).first()
        assert result is not None
        assert result[0].id == entity.id
        assert result[1].current == 50.0

    def test_query_first_empty(self):
        """测试 first() 空结果"""
        world = World()
        result = world.query(HealthComponent).first()
        assert result is None

    def test_query_count(self):
        """测试 count() 方法"""
        world = World()
        for _ in range(5):
            entity = world.create_entity()
            world.add_component(entity, HealthComponent())

        assert world.query(HealthComponent).count() == 5

    def test_query_caching(self):
        """测试查询缓存"""
        world = World()
        entity = world.create_entity()
        world.add_component(entity, HealthComponent())

        # 第一次查询
        result1 = list(world.query(HealthComponent))
        # 第二次查询（应从缓存获取）
        result2 = list(world.query(HealthComponent))

        assert len(result1) == len(result2) == 1
        # 缓存应在组件变更时清除
        world.add_component(entity, PositionComponent())
        assert len(world._query_cache) == 0

    def test_query_one(self):
        """测试 query_one 快捷方法"""
        world = World()
        entity = world.create_entity()
        world.add_component(entity, HealthComponent(current=75.0))

        result = world.query_one(HealthComponent)
        assert result is not None
        assert result[0].id == entity.id
        assert result[1].current == 75.0

    def test_query_entity_destruction_cache_clear(self):
        """测试实体删除清除缓存"""
        world = World()
        entity = world.create_entity()
        world.add_component(entity, HealthComponent())

        # 执行查询建立缓存
        list(world.query(HealthComponent))
        assert len(world._query_cache) > 0

        # 删除实体应清除缓存
        world.remove_entity(entity)
        assert len(world._query_cache) == 0

    def test_query_multiple_entities(self):
        """测试多个实体查询"""
        world = World()
        entities = []
        for i in range(3):
            entity = world.create_entity()
            world.add_component(entity, HealthComponent(current=float(i * 10)))
            world.add_component(entity, PositionComponent(x=float(i)))
            entities.append(entity)

        results = list(world.query(HealthComponent, PositionComponent))
        assert len(results) == 3
        for i, (entity, health, pos) in enumerate(results):
            assert health.current == float(i * 10)
            assert pos.x == float(i)

    def test_query_result_unpacking(self):
        """测试结果解包"""
        world = World()
        entity = world.create_entity()
        world.add_component(entity, HealthComponent(current=90.0))
        world.add_component(entity, PositionComponent(x=5.0, y=10.0))

        for e, health, pos in world.query(HealthComponent, PositionComponent):
            assert e.id == entity.id
            assert health.current == 90.0
            assert pos.x == 5.0
            assert pos.y == 10.0
