#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MemoryManagementSystem 测试

v4.0 新增 — 测试记忆管理系统的纯数据化迁移
"""

import pytest

from core.world import World
from core.entity import Entity

from human.components.cognitive.memory_component import MemoryComponent
from human.systems.cognitive.memory_management_system import MemoryManagementSystem


class TestMemoryManagementSystem:
    """测试记忆管理系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def memory(self):
        return MemoryComponent()

    def test_add_event(self, memory):
        """测试添加事件"""
        MemoryManagementSystem.add_event(
            memory, time=10.0, event_type="found_water",
            description="发现水源", impact=0.5
        )
        assert len(memory.events) == 1
        assert memory.events[0]["type"] == "found_water"
        assert memory.events[0]["impact"] == 0.5

    def test_add_event_limits(self, memory):
        """测试事件数量限制"""
        for i in range(110):
            MemoryManagementSystem.add_event(
                memory, time=float(i), event_type="test",
                description=f"事件{i}", impact=0.1
            )
        # 不应超过限制，但限制由 System.update 处理
        assert len(memory.events) == 110

    def test_get_recent_events(self, memory):
        """测试获取最近事件"""
        for i in range(10):
            MemoryManagementSystem.add_event(
                memory, time=float(i), event_type="test",
                description=f"事件{i}", impact=0.1
            )

        recent = MemoryManagementSystem.get_recent_events(memory, n=3)
        assert len(recent) == 3
        assert recent[0]["description"] == "事件7"

    def test_get_recent_events_by_type(self, memory):
        """测试按类型筛选事件"""
        MemoryManagementSystem.add_event(memory, 1.0, "found_water", "发现水", 0.5)
        MemoryManagementSystem.add_event(memory, 2.0, "found_food", "发现食物", 0.3)
        MemoryManagementSystem.add_event(memory, 3.0, "found_water", "再次发现水", 0.7)

        water_events = MemoryManagementSystem.get_recent_events(memory, event_type="found_water")
        assert len(water_events) == 2

    def test_get_event_sentiment(self, memory):
        """测试事件情感计算"""
        MemoryManagementSystem.add_event(memory, 1.0, "test", "正面", 0.8)
        MemoryManagementSystem.add_event(memory, 2.0, "test", "负面", -0.4)

        sentiment = MemoryManagementSystem.get_event_sentiment(memory, "test")
        assert sentiment == pytest.approx(0.2, abs=0.01)  # (0.8 - 0.4) / 2

    def test_record_place(self, memory):
        """测试记录地点"""
        MemoryManagementSystem.record_place(
            memory, pos=(10, 20), place_type="water_source",
            time=100.0, sentiment=0.8
        )

        assert (10, 20) in memory.places
        assert memory.places[(10, 20)]["type"] == "water_source"
        assert memory.places[(10, 20)]["sentiment"] == 0.8

    def test_record_place_update(self, memory):
        """测试地点记录更新"""
        MemoryManagementSystem.record_place(memory, (10, 20), "water_source", 100.0, 0.8)
        MemoryManagementSystem.record_place(memory, (10, 20), "water_source", 200.0, 0.6)

        # 访问次数增加
        assert memory.places[(10, 20)]["visits"] == 2
        # 情感加权平均
        assert memory.places[(10, 20)]["sentiment"] == pytest.approx(0.74, abs=0.01)

    def test_find_best_place(self, memory):
        """测试查找最佳地点"""
        MemoryManagementSystem.record_place(memory, (0, 0), "water_source", 100.0, 0.9)
        MemoryManagementSystem.record_place(memory, (100, 100), "water_source", 100.0, 0.5)

        best = MemoryManagementSystem.find_best_place_by_type(
            memory, "water_source", current_pos=(10, 10)
        )
        # 最近且情感最好的是 (0, 0)
        assert best == (0, 0)

    def test_find_best_place_no_match(self, memory):
        """测试无匹配地点"""
        result = MemoryManagementSystem.find_best_place_by_type(
            memory, "water_source", (0, 0)
        )
        assert result is None

    def test_record_person(self, memory):
        """测试记录人物"""
        MemoryManagementSystem.record_person(
            memory, entity_id=42, name="Alice",
            relationship="friend", time=100.0, trust=0.8
        )

        assert 42 in memory.people
        assert memory.people[42]["name"] == "Alice"
        assert memory.people[42]["trust"] == 0.8

    def test_update_relationship(self, memory):
        """测试更新关系"""
        MemoryManagementSystem.record_person(memory, 42, "Alice", "friend", 100.0, 0.5)
        MemoryManagementSystem.update_relationship(memory, 42, 200.0, trust_delta=0.2)

        assert memory.people[42]["trust"] == 0.7
        assert memory.people[42]["last_interaction"] == 200.0

    def test_update_relationship_clamped(self, memory):
        """测试关系值限制在 0-1"""
        MemoryManagementSystem.record_person(memory, 42, "Alice", "friend", 100.0, 0.9)
        MemoryManagementSystem.update_relationship(memory, 42, 200.0, trust_delta=0.2)

        assert memory.people[42]["trust"] == 1.0  # 上限

    def test_record_success(self, memory):
        """测试记录成功"""
        MemoryManagementSystem.record_success(memory, "find_water")
        assert memory.recent_successes["find_water"] == 1

    def test_system_decay(self, world):
        """测试系统衰减更新"""
        entity = world.create_entity()
        memory = MemoryComponent()
        memory.events.append({"time": 0, "type": "test", "impact": 1.0})
        world.add_component(entity, memory)

        system = MemoryManagementSystem()
        system.update(world, dt=1.0)

        # 情感应衰减
        assert memory.events[0]["impact"] < 1.0

    def test_system_limit(self, world):
        """测试系统限制历史长度"""
        entity = world.create_entity()
        memory = MemoryComponent()
        for i in range(110):
            memory.events.append({"time": float(i), "type": "test", "impact": 0.1})
        world.add_component(entity, memory)

        system = MemoryManagementSystem()
        system.update(world, dt=1.0)

        assert len(memory.events) <= memory.MAX_EVENTS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
