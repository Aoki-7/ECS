#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件总线测试
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import unittest

from core.event_bus import EventBus, Event


class TestEventBus(unittest.TestCase):
    """测试事件总线"""

    def setUp(self):
        EventBus.reset_instance()
        self.bus = EventBus.get_instance()

    def tearDown(self):
        EventBus.reset_instance()

    def test_singleton(self):
        """测试单例"""
        bus1 = EventBus.get_instance()
        bus2 = EventBus.get_instance()
        self.assertIs(bus1, bus2)

    def test_subscribe_and_publish(self):
        """测试订阅和发布"""
        received = []

        def handler(event):
            received.append(event.payload)

        self.bus.subscribe("test_event", handler)
        self.bus.publish("test_event", {"key": "value"})

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["key"], "value")

    def test_unsubscribe(self):
        """测试取消订阅"""
        received = []

        def handler(event):
            received.append(event)

        self.bus.subscribe("test_event", handler)
        self.bus.publish("test_event", {})
        self.assertEqual(len(received), 1)

        self.bus.unsubscribe("test_event", handler)
        self.bus.publish("test_event", {})
        self.assertEqual(len(received), 1)  # 不再接收

    def test_priority(self):
        """测试优先级"""
        order = []

        def handler_low(event):
            order.append("low")

        def handler_high(event):
            order.append("high")

        self.bus.subscribe("test_event", handler_low, priority=0)
        self.bus.subscribe("test_event", handler_high, priority=10)
        self.bus.publish("test_event", {})

        self.assertEqual(order, ["high", "low"])

    def test_once_subscription(self):
        """测试一次性订阅"""
        received = []

        def handler(event):
            received.append(event)

        self.bus.subscribe("test_event", handler, once=True)
        self.bus.publish("test_event", {})
        self.bus.publish("test_event", {})

        self.assertEqual(len(received), 1)

    def test_filter(self):
        """测试过滤函数"""
        received = []

        def handler(event):
            received.append(event)

        # 只接收 payload 中 important=True 的事件
        self.bus.subscribe(
            "test_event", handler,
            filter_fn=lambda e: e.payload.get("important", False)
        )

        self.bus.publish("test_event", {"important": False})
        self.bus.publish("test_event", {"important": True})

        self.assertEqual(len(received), 1)
        self.assertTrue(received[0].payload["important"])

    def test_history(self):
        """测试事件历史"""
        self.bus.publish("event_a", {"data": 1})
        self.bus.publish("event_b", {"data": 2})
        self.bus.publish("event_a", {"data": 3})

        history = self.bus.get_history("event_a")
        self.assertEqual(len(history), 2)

    def test_stats(self):
        """测试统计"""
        def handler(event):
            pass

        self.bus.subscribe("test_event", handler)
        self.bus.publish("test_event", {})
        self.bus.publish("test_event", {})

        stats = self.bus.get_stats()
        self.assertEqual(stats["published"], 2)
        self.assertEqual(stats["delivered"], 2)

    def test_multiple_handlers(self):
        """测试多个处理函数"""
        received_a = []
        received_b = []

        def handler_a(event):
            received_a.append(event)

        def handler_b(event):
            received_b.append(event)

        self.bus.subscribe("test_event", handler_a)
        self.bus.subscribe("test_event", handler_b)
        self.bus.publish("test_event", {})

        self.assertEqual(len(received_a), 1)
        self.assertEqual(len(received_b), 1)

    def test_event_object(self):
        """测试事件对象"""
        event = Event(
            event_type="test",
            payload={"key": "value"},
            source="test_source",
            priority=5,
        )

        self.assertEqual(event.event_type, "test")
        self.assertEqual(event.payload["key"], "value")
        self.assertEqual(event.source, "test_source")
        self.assertEqual(event.priority, 5)

        data = event.to_dict()
        self.assertIn("event_id", data)
        self.assertEqual(data["event_type"], "test")


class TestEventBusIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        EventBus.reset_instance()
        self.bus = EventBus.get_instance()

    def tearDown(self):
        EventBus.reset_instance()

    def test_entity_lifecycle_events(self):
        """测试实体生命周期事件"""
        events = []

        def on_created(event):
            events.append(("created", event.payload["entity_id"]))

        def on_destroyed(event):
            events.append(("destroyed", event.payload["entity_id"]))

        self.bus.subscribe("entity_created", on_created)
        self.bus.subscribe("entity_destroyed", on_destroyed)

        # 模拟实体创建和销毁
        self.bus.publish("entity_created", {"entity_id": 1, "type": "human"})
        self.bus.publish("entity_destroyed", {"entity_id": 1, "reason": "death"})

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0], ("created", 1))
        self.assertEqual(events[1], ("destroyed", 1))

    def test_memory_events(self):
        """测试记忆相关事件"""
        memories = []

        def on_memory_formed(event):
            memories.append(event.payload["concept_id"])

        self.bus.subscribe("memory_formed", on_memory_formed)
        self.bus.publish("memory_formed", {
            "subject_id": 1,
            "concept_id": "entity_42_stone",
            "formation_type": "direct",
        })

        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0], "entity_42_stone")


if __name__ == "__main__":
    unittest.main(verbosity=2)
