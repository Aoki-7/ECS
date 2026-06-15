#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
World 事件集成测试

验证 World.create_entity() 和 remove_entity() 触发事件。
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import unittest

from core.world import World
from core.event_bus import EventBus


class TestWorldEventIntegration(unittest.TestCase):
    """测试 World 与事件总线集成"""

    def setUp(self):
        EventBus.reset_instance()
        self.bus = EventBus.get_instance()
        self.world = World()

    def tearDown(self):
        EventBus.reset_instance()

    def test_create_entity_emits_event(self):
        """测试创建实体触发事件"""
        received = []

        def on_created(event):
            received.append(event.payload["entity_id"])

        self.bus.subscribe("entity_created", on_created)
        entity = self.world.create_entity()

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], entity.id)

    def test_remove_entity_emits_event(self):
        """测试删除实体触发事件"""
        received = []

        def on_destroyed(event):
            received.append(event.payload["entity_id"])

        self.bus.subscribe("entity_destroyed", on_destroyed)
        entity = self.world.create_entity()
        self.world.remove_entity(entity)

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], entity.id)

    def test_world_has_event_bus(self):
        """测试 World 可以访问事件总线"""
        bus = self.world.get_event_bus()
        self.assertIsNotNone(bus)
        self.assertIsInstance(bus, EventBus)


if __name__ == "__main__":
    unittest.main(verbosity=2)
