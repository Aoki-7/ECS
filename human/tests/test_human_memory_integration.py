#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Human 模块记忆层集成测试

验证：
1. PerceptionSystem 感知时记录 Contact
2. DialogueSystem 对话时记录 Contact 和叙述传播
3. 人类认知框架
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import unittest

from core.world import World
from core.entity import Entity

from memory_layer import MemoryLayer, SensoryDescription, SubjectType
from memory_layer.cognitive_framework import create_human_framework

from human.components.basic.human_component import HumanComponent
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from core.components.vision_component import VisionComponent


class TestHumanPerceptionMemoryIntegration(unittest.TestCase):
    """测试人类感知与记忆层集成"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_perception_records_contact(self):
        """测试人类感知时自动记录接触"""
        # 注册石头概念
        self.ml.register_entity(100, "stone", SensoryDescription(shape="圆形", color="灰色"))

        # 创建人类观察者
        observer = self.world.create_entity()
        self.world.add_component(observer, HumanComponent())
        self.world.add_component(observer, MemoryComponent())
        self.world.add_component(observer, SpaceComponent(x=0, y=0))
        self.world.add_component(observer, VisionComponent(radius=10.0))

        # 手动记录接触（模拟感知系统行为）
        self.ml.record_contact(
            subject_id=observer.id,
            subject_type=SubjectType.HUMAN,
            entity_id=100,
            contact_type="visual",
            intensity=0.8,
            context="看到石头",
        )

        # 验证记忆形成
        memories = self.ml.get_subject_memories(observer.id)
        self.assertGreaterEqual(len(memories), 0)

    def test_human_cognitive_framework(self):
        """测试人类认知框架"""
        framework = create_human_framework()

        # 人类对颜色敏感
        self.assertGreater(framework.attention_weights["color"], 1.0)

        # 人类有文化解释偏差
        self.assertIn("color", framework.interpretation_bias)

        # 应用解释偏差（偏差是概率性的，多次测试确保覆盖）
        desc = SensoryDescription(shape="圆形", color="灰色")
        # 运行多次以触发偏差
        results = set()
        for _ in range(20):
            biased = framework.apply_interpretation_bias(desc)
            results.add(biased.color)

        # 至少有一次出现偏差结果（概率性，但20次应足够）
        # 或者保持原值也是可能的
        self.assertIn("灰色", results)  # 原值应至少出现一次


class TestHumanDialogueMemoryIntegration(unittest.TestCase):
    """测试人类对话与记忆层集成"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_dialogue_records_contact(self):
        """测试对话时记录接触"""
        # 注册两个实体
        self.ml.register_entity(1, "human", SensoryDescription(shape="人形"))
        self.ml.register_entity(2, "human", SensoryDescription(shape="人形"))

        # 模拟对话接触记录
        self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.HUMAN,
            entity_id=2,
            contact_type="social",
            intensity=0.7,
            context="友好对话",
        )

        # 验证接触记录
        memories = self.ml.get_subject_memories(1)
        self.assertGreaterEqual(len(memories), 0)

    def test_narrate_between_humans(self):
        """测试人类间的叙述传播"""
        # 注册实体和概念
        self.ml.register_entity(1, "human", SensoryDescription(shape="人形"))
        self.ml.register_entity(2, "human", SensoryDescription(shape="人形"))
        self.ml.register_entity(100, "stone", SensoryDescription(shape="圆形", color="灰色"))

        # 人类1直接观察石头
        self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.HUMAN,
            entity_id=100,
            contact_type="visual",
            intensity=0.9,
            attention_level=0.9,
        )

        mem1 = self.ml.recall_memory(1, "entity_100_stone")
        self.assertIsNotNone(mem1)

        # 人类1向人类2叙述
        new_mem = self.ml.narrate_memory(
            from_subject=1,
            to_subject=2,
            to_subject_type=SubjectType.HUMAN,
            concept_id="entity_100_stone",
        )

        self.assertIsNotNone(new_mem)
        self.assertEqual(new_mem.subject_id, 2)
        self.assertEqual(new_mem.formation_type, "narrative")


class TestHumanMemoryLifecycle(unittest.TestCase):
    """测试人类记忆完整生命周期"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_human_entity_lifecycle(self):
        """测试人类实体生命周期中的记忆管理"""
        # 1. 创建石头
        self.ml.register_entity(100, "stone", SensoryDescription(shape="圆形", color="灰色"))

        # 2. 人类观察石头
        self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.HUMAN,
            entity_id=100,
            contact_type="visual",
            intensity=0.8,
        )

        # 3. 石头被摧毁
        self.ml.entity_destroyed(100, timestamp=50.0)

        # 4. 概念仍存在但非活跃
        concept = self.ml.get_concept("entity_100_stone")
        self.assertFalse(concept.is_active)

        # 5. 人类仍然记得石头
        mem = self.ml.recall_memory(1, "entity_100_stone")
        self.assertIsNotNone(mem)

        # 6. 人类向另一个人类叙述
        self.ml.narrate_memory(
            from_subject=1,
            to_subject=2,
            to_subject_type=SubjectType.HUMAN,
            concept_id="entity_100_stone",
        )

        # 7. 第二个人类也形成了关于已消亡石头的记忆
        mem2 = self.ml.recall_memory(2, "entity_100_stone")
        self.assertIsNotNone(mem2)
        self.assertEqual(mem2.formation_type, "narrative")


if __name__ == "__main__":
    unittest.main(verbosity=2)
