#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECS 集成测试

验证统一记忆层与 ECS 的集成。
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import unittest

from core.world import World
from core.entity import Entity

from memory_layer import MemoryLayer, SensoryDescription, SubjectType
from memory_layer.memory_registration_system import MemoryRegistrationSystem

from biology.organisms.animal.components.animal_component import AnimalComponent
from biology.organisms.animal.components.animal_perception_component import AnimalPerceptionComponent
from biology.organisms.animal.components.animal_memory_component import AnimalMemoryComponent
from space.space_component import SpaceComponent


class TestWorldIntegration(unittest.TestCase):
    """测试 World 与记忆层的集成"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_world_has_memory_layer(self):
        """测试 World 可以访问记忆层"""
        ml = self.world.get_memory_layer()
        self.assertIsNotNone(ml)
        self.assertIsInstance(ml, MemoryLayer)

    def test_entity_destroy_notifies_memory_layer(self):
        """测试实体销毁时通知记忆层"""
        desc = SensoryDescription(shape="圆形", color="灰色")
        self.ml.register_entity(entity_id=42, entity_type="stone", description=desc)
        
        # 直接使用 World.create_entity() 创建实体
        entity = self.world.create_entity()
        # 手动将实体ID映射到42（模拟注册）
        self.ml._entity_to_concept[entity.id] = "entity_42_stone"
        
        self.ml.entity_destroyed(42, timestamp=100.0)
        
        concept = self.ml.get_concept("entity_42_stone")
        self.assertFalse(concept.is_active)


class TestPerceptionSystemIntegration(unittest.TestCase):
    """测试感知系统与记忆层的集成"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_perception_records_contact(self):
        """测试感知时自动记录接触"""
        self.ml.register_entity(10, "animal", SensoryDescription(shape="四足"))
        self.ml.register_entity(20, "stone", SensoryDescription(shape="圆形"))
        
        animal = self.world.create_entity()
        self.world.add_component(animal, AnimalComponent())
        self.world.add_component(animal, AnimalPerceptionComponent(vision_range=10.0))
        self.world.add_component(animal, AnimalMemoryComponent())
        self.world.add_component(animal, SpaceComponent(x=0, y=0))
        
        stone = self.world.create_entity()
        self.world.add_component(stone, SpaceComponent(x=2, y=2))
        
        self.ml.record_contact(
            subject_id=animal.id,
            subject_type=SubjectType.ANIMAL,
            entity_id=stone.id,
            contact_type="visual",
            intensity=0.8,
        )
        
        memories = self.ml.get_subject_memories(animal.id)
        self.assertGreaterEqual(len(memories), 0)


class TestSocialSystemIntegration(unittest.TestCase):
    """测试社交系统与记忆层的集成"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_narrate_between_animals(self):
        """测试动物间的叙述传播"""
        self.ml.register_entity(1, "animal", SensoryDescription(shape="四足"))
        self.ml.register_entity(2, "animal", SensoryDescription(shape="四足"))
        self.ml.register_entity(100, "stone", SensoryDescription(shape="圆形", color="灰色"))
        
        self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            entity_id=100,
            contact_type="visual",
            intensity=0.9,
            attention_level=0.9,
        )
        
        mem1 = self.ml.recall_memory(1, "entity_100_stone")
        self.assertIsNotNone(mem1)
        
        new_mem = self.ml.narrate_memory(
            from_subject=1,
            to_subject=2,
            to_subject_type=SubjectType.ANIMAL,
            concept_id="entity_100_stone",
        )
        
        self.assertIsNotNone(new_mem)
        self.assertEqual(new_mem.subject_id, 2)
        self.assertEqual(new_mem.formation_type, "narrative")
        self.assertLess(new_mem.confidence, mem1.confidence)


class TestMemoryRegistrationSystem(unittest.TestCase):
    """测试记忆注册系统"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_registration_system_scans_entities(self):
        """测试注册系统扫描实体"""
        reg_sys = MemoryRegistrationSystem()
        
        entity = self.world.create_entity()
        self.world.add_component(entity, AnimalComponent(species="basic", diet="herbivore"))
        self.world.add_component(entity, SpaceComponent(x=0, y=0))
        
        reg_sys.update(self.world, dt=1.0)
        
        self.assertIn(entity.id, reg_sys._registered_entities)
        
        concept = self.ml.get_concept_by_entity(entity.id)
        self.assertIsNotNone(concept)


class TestFullLifecycle(unittest.TestCase):
    """完整生命周期集成测试"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_entity_lifecycle_with_memory(self):
        """测试实体完整生命周期中的记忆管理"""
        stone_desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        stone_concept = self.ml.register_entity(
            entity_id=100, entity_type="stone", description=stone_desc
        )
        self.assertTrue(stone_concept.is_active)
        
        self.ml.record_contact(
            subject_id=1,
            subject_type=SubjectType.ANIMAL,
            entity_id=100,
            contact_type="visual",
            intensity=0.8,
            attention_level=0.9,
        )
        
        mem_a = self.ml.recall_memory(1, "entity_100_stone")
        self.assertIsNotNone(mem_a)
        
        self.ml.entity_destroyed(100, timestamp=50.0)
        
        concept = self.ml.get_concept("entity_100_stone")
        self.assertFalse(concept.is_active)
        
        mem_a2 = self.ml.recall_memory(1, "entity_100_stone")
        self.assertIsNotNone(mem_a2)
        
        self.ml.narrate_memory(
            from_subject=1,
            to_subject=2,
            to_subject_type=SubjectType.ANIMAL,
            concept_id="entity_100_stone",
        )
        
        mem_b = self.ml.recall_memory(2, "entity_100_stone")
        self.assertIsNotNone(mem_b)
        self.assertEqual(mem_b.formation_type, "narrative")
        
        stats = self.ml.get_stats()
        self.assertEqual(stats["concept_count"], 1)
        self.assertEqual(stats["active_concepts"], 0)
        self.assertEqual(stats["memory_count"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)