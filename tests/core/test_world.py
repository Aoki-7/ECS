#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
World 核心 ECS 框架测试

覆盖：Entity CRUD、Component CRUD、get_components 批量查询、query cache、System 调度
"""

import pytest
from dataclasses import dataclass

from core.world import World
from core.entity import Entity
from core.component import Component
from core.system import System


@dataclass(slots=True)
class HealthComponent(Component):
    hp: int = 100


@dataclass(slots=True)
class PositionComponent(Component):
    x: float = 0.0
    y: float = 0.0


class DummySystem(System):
    def __init__(self):
        super().__init__()
        self.update_count = 0

    def update(self, world, dt=1.0):
        super().update(world, dt)
        self.update_count += 1


class TestWorldEntityCRUD:
    """实体增删改查"""

    def test_create_entity(self):
        world = World()
        entity = world.create_entity()
        assert entity.id >= 0
        assert world.has_entity(entity)
        assert world.query_entity(entity.id) == entity

    def test_remove_entity(self):
        world = World()
        entity = world.create_entity()
        world.remove_entity(entity)
        assert not world.has_entity(entity)
        assert world.query_entity(entity.id) is None

    def test_remove_entity_cleans_components(self):
        world = World()
        entity = world.create_entity()
        world.add_component(entity, HealthComponent(hp=50))
        world.remove_entity(entity)
        assert world.get_component(entity, HealthComponent) is None

    def test_entity_generation_check(self):
        world = World()
        entity = world.create_entity()
        world.remove_entity(entity)
        # 删除后旧引用不再有效
        assert not world.has_entity(entity)


class TestWorldComponentCRUD:
    """组件增删改查"""

    def test_add_and_get_component(self):
        world = World()
        entity = world.create_entity()
        comp = HealthComponent(hp=80)
        world.add_component(entity, comp)
        assert world.get_component(entity, HealthComponent) == comp

    def test_add_component_invalidates_query_cache(self):
        world = World()
        e1 = world.create_entity()
        world.add_component(e1, HealthComponent())

        # 第一次查询，建立缓存
        results = list(world.get_components(HealthComponent))
        assert len(results) == 1

        # 添加新组件应使缓存失效
        e2 = world.create_entity()
        world.add_component(e2, HealthComponent())
        results = list(world.get_components(HealthComponent))
        assert len(results) == 2

    def test_remove_component(self):
        world = World()
        entity = world.create_entity()
        world.add_component(entity, HealthComponent())
        world.remove_component(entity, HealthComponent)
        assert world.get_component(entity, HealthComponent) is None

    def test_get_component_missing_returns_none(self):
        world = World()
        entity = world.create_entity()
        assert world.get_component(entity, HealthComponent) is None


class TestWorldGetComponents:
    """批量组件查询"""

    def test_single_component_query(self):
        world = World()
        e1 = world.create_entity()
        e2 = world.create_entity()
        world.add_component(e1, HealthComponent(hp=10))
        world.add_component(e2, HealthComponent(hp=20))

        results = list(world.get_components(HealthComponent))
        assert len(results) == 2
        hps = {comp.hp for _, [comp] in results}
        assert hps == {10, 20}

    def test_multi_component_query(self):
        world = World()
        e1 = world.create_entity()
        e2 = world.create_entity()
        e3 = world.create_entity()

        world.add_component(e1, HealthComponent())
        world.add_component(e1, PositionComponent())

        world.add_component(e2, HealthComponent())
        # e2 无 PositionComponent

        world.add_component(e3, HealthComponent())
        world.add_component(e3, PositionComponent())

        results = list(world.get_components(HealthComponent, PositionComponent))
        assert len(results) == 2
        ids = {entity.id for entity, _ in results}
        assert ids == {e1.id, e3.id}

    def test_query_cache_reuse(self):
        world = World()
        e = world.create_entity()
        world.add_component(e, HealthComponent())

        r1 = list(world.get_components(HealthComponent))
        r2 = list(world.get_components(HealthComponent))
        assert len(r1) == len(r2) == 1


class TestWorldSystemScheduling:
    """系统注册与调度"""

    def test_add_system_and_update(self):
        world = World()
        sys = DummySystem()
        world.add_system(sys)
        world.update(dt=1.0)
        assert sys.update_count == 1

    def test_system_priority_order(self):
        world = World()
        order = []

        class SysA(System):
            priority = 1
            def update(self, world, dt=1.0):
                order.append("A")

        class SysB(System):
            priority = 2
            def update(self, world, dt=1.0):
                order.append("B")

        world.add_system(SysB())
        world.add_system(SysA())
        world.update(dt=1.0)
        assert order == ["A", "B"]

    def test_get_system(self):
        world = World()
        sys = DummySystem()
        world.add_system(sys)
        assert world.get_system(DummySystem) == sys
        assert world.get_system(System) == sys  # 基类查询也命中

    def test_tick_interval_skip(self):
        world = World()
        sys = DummySystem()
        sys.tick_interval = 2
        world.add_system(sys)

        world.update(dt=1.0)  # tick_count = 1，跳过（1 % 2 != 0）
        assert sys.update_count == 0
        world.update(dt=1.0)  # tick_count = 2，执行（2 % 2 == 0）
        assert sys.update_count == 1

    def test_system_error_isolation(self):
        world = World()

        class BrokenSystem(System):
            def update(self, world, dt=1.0):
                raise RuntimeError("broken")

        class GoodSystem(System):
            def __init__(self):
                super().__init__()
                self.ran = False
            def update(self, world, dt=1.0):
                self.ran = True

        good = GoodSystem()
        world.add_system(BrokenSystem())
        world.add_system(good)
        world.update(dt=1.0)
        assert good.ran  # 一个系统崩溃不应阻止其他系统


class TestWorldEntity:
    """世界实体访问"""

    def test_world_entity(self):
        world = World()
        assert world.get_world_entity() is None

        we = Entity.create()
        world.set_world_entity(we)
        assert world.get_world_entity() == we

    def test_world_component(self):
        from world.world_entity import WorldEntity
        world = World()
        we = world.create_entity()  # 使用 world.create_entity() 而非 WorldEntity()
        world.set_world_entity(we)
        world.add_component(we, HealthComponent(hp=999))
        assert world.get_world_component(HealthComponent).hp == 999


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
