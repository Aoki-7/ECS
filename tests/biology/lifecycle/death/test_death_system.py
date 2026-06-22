#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
死亡流程与死亡档案系统测试

覆盖：
- DeathSystem：PendingDeath → DeadTag/DeathReason/DeathTime/CorpseComponent
- DeathArchiveSystem：死亡实体归档、腐烂进度同步
"""

import pytest
from dataclasses import dataclass

from core.world import World
from core.component import Component
from world.world_entity import WorldEntity

from biology.lifecycle.death.components.pending_death_component import PendingDeathComponent
from biology.lifecycle.death.components.dead_tag_component import DeadTagComponent
from biology.lifecycle.death.components.death_reason_component import DeathReasonComponent
from biology.lifecycle.death.components.death_time_component import DeathTimeComponent
from biology.lifecycle.death.systems.death_system import DeathSystem
from biology.lifecycle.corpse.components.corpse_component import CorpseComponent

from death_archive.components.death_archive_component import DeathArchiveComponent
from death_archive.components.record_entry import RecordEntry
from death_archive.systems.death_archive_system import DeathArchiveSystem


@dataclass(slots=True)
class DummyTimeComponent(Component):
    total_hours: float = 100.0


class TestDeathSystem:
    """死亡执行系统测试"""

    def _make_world(self):
        world = World()
        we = world.create_entity()
        world.add_component(we, DummyTimeComponent(total_hours=42.0))
        world.set_world_entity(we)
        return world

    def test_death_system_executes_death(self):
        world = self._make_world()
        entity = world.create_entity()
        world.add_component(entity, PendingDeathComponent(
            reason="starvation", source_system="test", priority=1
        ))

        system = DeathSystem()
        system.update(world, dt=1.0)

        assert world.get_component(entity, DeadTagComponent) is not None
        assert world.get_component(entity, DeathReasonComponent) is not None
        assert world.get_component(entity, DeathTimeComponent) is not None
        assert world.get_component(entity, CorpseComponent) is not None
        # PendingDeath 应被移除
        assert world.get_component(entity, PendingDeathComponent) is None

    def test_death_reason_recorded(self):
        world = self._make_world()
        entity = world.create_entity()
        world.add_component(entity, PendingDeathComponent(
            reason="old_age", source_system="senescence", priority=5
        ))

        system = DeathSystem()
        system.update(world, dt=1.0)

        reason_comp = world.get_component(entity, DeathReasonComponent)
        assert reason_comp.primary_reason == "old_age"
        assert reason_comp.primary_source == "senescence"

    def test_death_deduplication(self):
        world = self._make_world()
        entity = world.create_entity()
        world.add_component(entity, DeadTagComponent())
        world.add_component(entity, PendingDeathComponent(
            reason="starvation", source_system="test", priority=1
        ))

        system = DeathSystem()
        system.update(world, dt=1.0)

        # 已有 DeadTag 的实体不应重复处理
        # PendingDeath 应被清理（update 中的 dedup 逻辑会移除它）
        assert world.get_component(entity, PendingDeathComponent) is None

    def test_corpse_component_building(self):
        world = self._make_world()
        entity = world.create_entity()
        world.add_component(entity, PendingDeathComponent(
            reason="test", source_system="test", priority=1
        ))

        system = DeathSystem()
        system.update(world, dt=1.0)

        corpse = world.get_component(entity, CorpseComponent)
        assert corpse is not None
        assert corpse.original_entity_id == entity.id
        assert corpse.decay_progress == 0.0


class TestDeathArchiveSystem:
    """死亡档案系统测试"""

    def _make_world(self):
        world = World()
        we = world.create_entity()
        world.add_component(we, DummyTimeComponent(total_hours=100.0))
        world.set_world_entity(we)
        return world

    def _kill_entity(self, world, reason="test"):
        """辅助方法：让实体死亡并执行死亡流程"""
        entity = world.create_entity()
        world.add_component(entity, PendingDeathComponent(
            reason=reason, source_system="test", priority=1
        ))
        death_sys = DeathSystem()
        death_sys.update(world, dt=1.0)
        return entity

    def test_archive_new_death(self):
        world = self._make_world()
        archive_sys = DeathArchiveSystem()
        archive_sys.on_add(world)

        entity = self._kill_entity(world, reason="starvation")

        archive_sys.update(world, dt=1.0)

        archive = world.get_world_component(DeathArchiveComponent)
        assert archive.total_deaths == 1
        assert entity.id in archive.index_by_entity
        record = archive.records[archive.index_by_entity[entity.id]]
        assert record.death_reason == "starvation"
        assert record.is_decayed is False

    def test_archive_deduplication(self):
        world = self._make_world()
        archive_sys = DeathArchiveSystem()
        archive_sys.on_add(world)

        entity = self._kill_entity(world, reason="old_age")
        archive_sys.update(world, dt=1.0)
        archive_sys.update(world, dt=1.0)  # 再次执行，不应重复归档

        archive = world.get_world_component(DeathArchiveComponent)
        assert archive.total_deaths == 1
        assert len(archive.records) == 1

    def test_archive_multiple_deaths(self):
        world = self._make_world()
        archive_sys = DeathArchiveSystem()
        archive_sys.on_add(world)

        e1 = self._kill_entity(world, reason="starvation")
        e2 = self._kill_entity(world, reason="old_age")
        archive_sys.update(world, dt=1.0)

        archive = world.get_world_component(DeathArchiveComponent)
        assert archive.total_deaths == 2
        assert archive.counters.get("starvation") == 1
        assert archive.counters.get("old_age") == 1

    def test_statistics_api(self):
        world = self._make_world()
        archive_sys = DeathArchiveSystem()
        archive_sys.on_add(world)

        self._kill_entity(world, reason="starvation")
        self._kill_entity(world, reason="starvation")
        self._kill_entity(world, reason="combat")
        archive_sys.update(world, dt=1.0)

        stats = archive_sys.get_statistics(world)
        assert stats["total_deaths"] == 3
        assert stats["counters"]["starvation"] == 2
        assert stats["counters"]["combat"] == 1

    def test_query_by_reason(self):
        world = self._make_world()
        archive_sys = DeathArchiveSystem()
        archive_sys.on_add(world)

        self._kill_entity(world, reason="starvation")
        self._kill_entity(world, reason="old_age")
        archive_sys.update(world, dt=1.0)

        records = archive_sys.get_records_by_reason(world, "starvation")
        assert len(records) == 1
        assert records[0].death_reason == "starvation"

    def test_query_by_time_range(self):
        world = self._make_world()
        archive_sys = DeathArchiveSystem()
        archive_sys.on_add(world)

        self._kill_entity(world, reason="A")
        self._kill_entity(world, reason="B")
        archive_sys.update(world, dt=1.0)

        records = archive_sys.get_records_by_time_range(world, 0.0, 200.0)
        assert len(records) == 2

        records = archive_sys.get_records_by_time_range(world, 500.0, 1000.0)
        assert len(records) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
