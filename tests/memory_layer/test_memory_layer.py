#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一记忆层单元测试

覆盖：
- 概念注册与消亡
- 接触记录与记忆形成
- 记忆回忆与传播
- 遗忘机制
- 序列化/反序列化
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import unittest

from memory_layer import (
    MemoryLayer,
    Concept,
    ConceptType,
    MemoryInstance,
    SubjectType,
    ContactRecord,
    SensoryDescription,
    EmotionalTag,
    AssociationLink,
)


class TestSensoryDescription(unittest.TestCase):
    """测试感官描述"""

    def test_creation(self):
        desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        self.assertEqual(desc.shape, "圆形")
        self.assertEqual(desc.color, "灰色")
        self.assertIsNone(desc.smell)

    def test_to_text(self):
        desc = SensoryDescription(shape="圆形", color="灰色")
        text = desc.to_text()
        self.assertIn("圆形", text)
        self.assertIn("灰色", text)

    def test_merge(self):
        desc1 = SensoryDescription(shape="圆形", color="灰色")
        desc2 = SensoryDescription(shape="方形", color="红色", texture="光滑")
        merged = desc1.merge_with(desc2, weight=0.6)
        # weight > 0.5，应优先采用 desc2
        self.assertEqual(merged.shape, "方形")
        self.assertEqual(merged.color, "红色")
        self.assertEqual(merged.texture, "光滑")

    def test_serialization(self):
        desc = SensoryDescription(shape="圆形", color="灰色", temperature="冰凉")
        data = desc.to_dict()
        restored = SensoryDescription.from_dict(data)
        self.assertEqual(restored.shape, "圆形")
        self.assertEqual(restored.temperature, "冰凉")


class TestEmotionalTag(unittest.TestCase):
    """测试情感标签"""

    def test_transfer_with_loss(self):
        emotion = EmotionalTag(primary="fear", intensity=0.9, reason="被攻击")
        transferred = emotion.transfer_with_loss(loss_factor=0.3)
        self.assertEqual(transferred.primary, "fear")
        self.assertAlmostEqual(transferred.intensity, 0.63, places=2)
        self.assertIn("听说", transferred.reason)


class TestConcept(unittest.TestCase):
    """测试客观概念"""

    def test_creation(self):
        desc = SensoryDescription(shape="圆形", color="灰色")
        concept = Concept(
            concept_id="entity_42_stone",
            name="石头_42",
            concept_type=ConceptType.ENTITY,
            canonical_description=desc,
            source_entity_id=42,
            source_entity_type="stone",
        )
        self.assertTrue(concept.is_active)
        self.assertEqual(concept.source_entity_id, 42)

    def test_mark_destroyed(self):
        desc = SensoryDescription(shape="圆形")
        concept = Concept(
            concept_id="entity_42_stone",
            name="石头_42",
            concept_type=ConceptType.ENTITY,
            canonical_description=desc,
            source_entity_id=42,
        )
        concept.mark_destroyed(100.0)
        self.assertFalse(concept.is_active)
        self.assertEqual(concept.destroyed_at, 100.0)

    def test_serialization(self):
        desc = SensoryDescription(shape="圆形", color="灰色")
        concept = Concept(
            concept_id="entity_42_stone",
            name="石头_42",
            concept_type=ConceptType.ENTITY,
            canonical_description=desc,
            source_entity_id=42,
            physical_properties={"hardness": 50},
        )
        data = concept.to_dict()
        restored = Concept.from_dict(data)
        self.assertEqual(restored.concept_id, "entity_42_stone")
        self.assertEqual(restored.physical_properties["hardness"], 50)


class TestMemoryInstance(unittest.TestCase):
    """测试主观记忆"""

    def test_creation(self):
        memory = MemoryInstance(
            memory_id="mem_001",
            concept_id="entity_42_stone",
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            sensory_impression=SensoryDescription(shape="圆形"),
            emotional_tag=EmotionalTag(primary="disgust", intensity=0.8),
        )
        self.assertEqual(memory.confidence, 1.0)
        self.assertEqual(memory.formation_type, "direct")

    def test_decay(self):
        memory = MemoryInstance(
            memory_id="mem_001",
            concept_id="entity_42_stone",
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            clarity=1.0,
            confidence=1.0,
        )
        memory.decay(rate=0.1)
        self.assertAlmostEqual(memory.clarity, 0.9, places=2)
        self.assertAlmostEqual(memory.confidence, 0.95, places=2)

    def test_recall(self):
        memory = MemoryInstance(
            memory_id="mem_001",
            concept_id="entity_42_stone",
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            clarity=0.5,
            recall_count=0,
        )
        memory.recall(timestamp=100.0)
        self.assertEqual(memory.last_recall, 100.0)
        self.assertEqual(memory.recall_count, 1)
        self.assertGreater(memory.clarity, 0.5)

    def test_importance(self):
        memory = MemoryInstance(
            memory_id="mem_001",
            concept_id="entity_42_stone",
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            emotional_tag=EmotionalTag(primary="fear", intensity=1.0),
            clarity=1.0,
            confidence=1.0,
            recall_count=10,
        )
        importance = memory.calculate_importance()
        self.assertGreater(importance, 0.5)


class TestMemoryLayer(unittest.TestCase):
    """测试记忆层管理器"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_register_entity(self):
        desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        concept = self.ml.register_entity(
            entity_id=42,
            entity_type="stone",
            description=desc,
            physical_props={"hardness": 50},
        )
        self.assertEqual(concept.concept_id, "entity_42_stone")
        self.assertTrue(concept.is_active)

        # 验证可以通过 entity_id 查询
        found = self.ml.get_concept_by_entity(42)
        self.assertIsNotNone(found)
        self.assertEqual(found.concept_id, concept.concept_id)

    def test_entity_destroyed(self):
        desc = SensoryDescription(shape="圆形")
        self.ml.register_entity(entity_id=42, entity_type="stone", description=desc)
        self.ml.entity_destroyed(42, timestamp=100.0)

        concept = self.ml.get_concept_by_entity(42)
        self.assertFalse(concept.is_active)
        self.assertEqual(concept.destroyed_at, 100.0)

    def test_create_abstract_concept(self):
        desc = SensoryDescription(shape="巨大", color="金色")
        concept = self.ml.create_abstract_concept(
            name="龙",
            description=desc,
            concept_type=ConceptType.MYTH,
        )
        self.assertEqual(concept.name, "龙")
        self.assertEqual(concept.concept_type, ConceptType.MYTH)
        self.assertFalse(concept.is_active)
        self.assertIsNone(concept.source_entity_id)

    def test_record_contact_and_form_memory(self):
        # 注册实体
        desc = SensoryDescription(shape="圆形", color="灰色")
        self.ml.register_entity(entity_id=42, entity_type="stone", description=desc)

        # 记录接触
        contact = self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            entity_id=42,
            contact_type="visual",
            intensity=0.8,
            attention_level=0.9,
        )
        self.assertIsNotNone(contact)

        # 验证记忆自动形成
        memory = self.ml.recall_memory(subject_id=1, concept_id="entity_42_stone")
        self.assertIsNotNone(memory)
        self.assertEqual(memory.subject_id, 1)
        self.assertEqual(memory.formation_type, "direct")
        self.assertGreater(memory.confidence, 0.5)

    def test_recall_updates_stats(self):
        desc = SensoryDescription(shape="圆形")
        self.ml.register_entity(entity_id=42, entity_type="stone", description=desc)
        self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            entity_id=42,
            contact_type="visual",
        )

        memory = self.ml.recall_memory(1, "entity_42_stone")
        self.assertEqual(memory.recall_count, 1)

        memory = self.ml.recall_memory(1, "entity_42_stone")
        self.assertEqual(memory.recall_count, 2)

    def test_narrate_memory(self):
        # 注册实体
        desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        self.ml.register_entity(entity_id=42, entity_type="stone", description=desc)

        # 生物A形成直接记忆
        self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            entity_id=42,
            contact_type="visual",
            intensity=0.9,
            attention_level=0.9,
        )

        # 生物A向生物B叙述
        new_memory = self.ml.narrate_memory(
            from_subject=1,
            to_subject=2,
            to_subject_type=SubjectType.ANIMAL,
            concept_id="entity_42_stone",
        )
        self.assertIsNotNone(new_memory)
        self.assertEqual(new_memory.subject_id, 2)
        self.assertEqual(new_memory.formation_type, "narrative")
        self.assertEqual(new_memory.source_subject_id, 1)

        # 间接记忆的确信度应更低
        original = self.ml.recall_memory(1, "entity_42_stone")
        self.assertLess(new_memory.confidence, original.confidence)

    def test_forgetting(self):
        desc = SensoryDescription(shape="圆形")
        self.ml.register_entity(entity_id=42, entity_type="stone", description=desc)
        self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            entity_id=42,
            contact_type="visual",
            intensity=0.1,  # 低强度，容易遗忘
            attention_level=0.1,
        )

        # 强制多次衰减
        memory = self.ml.recall_memory(1, "entity_42_stone")
        for _ in range(100):
            memory.decay(rate=0.1)

        # 应用遗忘
        forgotten = self.ml.apply_forgetting(subject_id=1, decay_rate=0.5)
        self.assertGreaterEqual(forgotten, 0)

    def test_capacity_limit(self):
        desc = SensoryDescription(shape="圆形")

        # 创建多个实体和记忆
        for i in range(10):
            self.ml.register_entity(entity_id=100 + i, entity_type="stone", description=desc)
            self.ml.record_contact(
                subject_id=1,
                subject_type=SubjectType.ANIMAL,
                entity_id=100 + i,
                contact_type="visual",
            )

        # 设置容量上限为5
        forgotten = self.ml.enforce_capacity_limit(subject_id=1, max_memories=5)
        self.assertEqual(forgotten, 5)

        memories = self.ml.get_subject_memories(1)
        self.assertEqual(len(memories), 5)

    def test_serialization(self):
        desc = SensoryDescription(shape="圆形", color="灰色")
        self.ml.register_entity(entity_id=42, entity_type="stone", description=desc)
        self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            entity_id=42,
            contact_type="visual",
        )

        # 序列化
        data = self.ml.serialize()
        self.assertIn("concepts", data)
        self.assertIn("memories", data)
        self.assertIn("contacts", data)

        # 反序列化到新实例
        MemoryLayer.reset_instance()
        new_ml = MemoryLayer.get_instance()
        new_ml.deserialize(data)

        self.assertEqual(len(new_ml.get_all_concepts()), 1)
        self.assertEqual(len(new_ml.get_all_memories()), 1)

    def test_stats(self):
        desc = SensoryDescription(shape="圆形")
        self.ml.register_entity(entity_id=42, entity_type="stone", description=desc)
        self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            entity_id=42,
            contact_type="visual",
        )

        stats = self.ml.get_stats()
        self.assertEqual(stats["concept_count"], 1)
        self.assertEqual(stats["active_concepts"], 1)
        self.assertEqual(stats["memory_count"], 1)
        self.assertEqual(stats["subjects"], 1)


class TestMemoryPropagationDistortion(unittest.TestCase):
    """测试记忆传播失真"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_multiple_narration_distortion(self):
        """测试多次叙述传播后的失真"""
        # 注册实体：圆形灰色光滑石头
        desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        self.ml.register_entity(entity_id=42, entity_type="stone", description=desc)

        # 生物0直接观察（高注意力，高确信度）
        self.ml.record_contact(
            subject_id=0,
            subject_type=SubjectType.ANIMAL,
            entity_id=42,
            contact_type="visual",
            intensity=0.9,
            attention_level=0.95,
        )

        # 链式传播：0→1→2→3
        for i in range(3):
            self.ml.narrate_memory(
                from_subject=i,
                to_subject=i + 1,
                to_subject_type=SubjectType.ANIMAL,
                concept_id="entity_42_stone",
            )

        # 检查失真累积
        memories = []
        for i in range(4):
            mem = self.ml.recall_memory(i, "entity_42_stone")
            memories.append(mem)

        # 确信度应递减
        self.assertGreater(memories[0].confidence, memories[1].confidence)
        self.assertGreater(memories[1].confidence, memories[2].confidence)

        # 扭曲度应递增
        self.assertLess(memories[0].distortion_level, memories[1].distortion_level)
        self.assertLess(memories[1].distortion_level, memories[2].distortion_level)

        # 清晰度应递减
        self.assertGreater(memories[0].clarity, memories[1].clarity)


if __name__ == "__main__":
    unittest.main(verbosity=2)
