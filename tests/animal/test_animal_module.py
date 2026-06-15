#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物模块测试 — 适配 Component 纯数据化

v3.9 适配：
- AnimalMemoryComponent 方法迁移到 AnimalMemorySystem
- AnimalReproductionComponent 方法迁移到 AnimalReproductionSystem
"""

import unittest
from core.world import World
from animal.components.animal_component import AnimalComponent
from animal.components.animal_learning_component import AnimalLearningComponent
from animal.components.animal_memory_component import AnimalMemoryComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from animal.components.animal_perception_component import AnimalPerceptionComponent
from animal.components.animal_reproduction_component import AnimalReproductionComponent
from animal.components.animal_social_component import AnimalSocialComponent
from animal.components.animal_territory_component import AnimalTerritoryComponent
from animal.systems.animal_learning_system import AnimalLearningSystem
from animal.systems.animal_memory_system import AnimalMemorySystem
from animal.systems.animal_reproduction_system import AnimalReproductionSystem
from space.space_component import SpaceComponent
from biology.lifecycle.components.energy_component import EnergyComponent


class TestAnimalComponents(unittest.TestCase):
    """测试动物组件"""

    def test_animal_component(self):
        """测试动物基础组件"""
        animal = AnimalComponent()
        self.assertIn(animal.gender, ["male", "female"])
        self.assertEqual(animal.age, 0)

    def test_animal_learning_component(self):
        """测试学习组件"""
        learn = AnimalLearningComponent()
        AnimalLearningSystem.record_behavior(learn, "graze", "food_rich", 0.8)
        AnimalLearningSystem.record_behavior(learn, "graze", "food_rich", 0.9)

        # 两次记录应合并
        self.assertEqual(len(learn.behavior_records), 1)
        self.assertAlmostEqual(AnimalLearningSystem.get_behavior_value(learn, "graze", "food_rich"), 0.85, places=1)

    def test_animal_memory_component(self):
        """测试记忆组件"""
        memory = AnimalMemoryComponent(max_memories=3)
        AnimalMemorySystem.add_memory(memory, 1.0, 2.0, "food", entity_id=10, value=0.8, timestamp=0)
        AnimalMemorySystem.add_memory(memory, 3.0, 4.0, "water", entity_id=20, value=0.6, timestamp=0)

        recalled = AnimalMemorySystem.recall_by_type(memory, "food")
        self.assertIsNotNone(recalled)
        self.assertEqual(recalled.entity_id, 10)

        # 测试容量限制
        AnimalMemorySystem.add_memory(memory, 5.0, 6.0, "shelter", value=0.9, timestamp=0)
        AnimalMemorySystem.add_memory(memory, 7.0, 8.0, "food", value=0.7, timestamp=0)
        self.assertLessEqual(len(memory.memories), 3)

    def test_animal_reproduction_component(self):
        """测试繁殖组件"""
        repro = AnimalReproductionComponent()
        self.assertTrue(AnimalReproductionSystem.is_ready(repro, 0))
        self.assertFalse(repro.is_pregnant)

        AnimalReproductionSystem.record_reproduction(repro, 10)
        self.assertEqual(repro.reproduction_count, 1)
        self.assertFalse(AnimalReproductionSystem.is_ready(repro, 10))
        self.assertTrue(AnimalReproductionSystem.is_ready(repro, 50))

        AnimalReproductionSystem.start_pregnancy(repro, 20, mate_id=5)
        self.assertTrue(repro.is_pregnant)
        self.assertEqual(repro.mate_id, 5)
        self.assertFalse(AnimalReproductionSystem.check_birth_ready(repro, 20))
        self.assertTrue(AnimalReproductionSystem.check_birth_ready(repro, 80))

        AnimalReproductionSystem.give_birth(repro)
        self.assertFalse(repro.is_pregnant)

    def test_animal_territory_component(self):
        terr = AnimalTerritoryComponent(center_x=5.0, center_y=5.0, radius=3.0)
        self.assertTrue(terr.is_inside(5.0, 5.0))
        self.assertTrue(terr.is_inside(7.0, 5.0))
        self.assertFalse(terr.is_inside(10.0, 10.0))

        terr.add_intruder(99)
        self.assertIn(99, terr.intruders)
        terr.remove_intruder(99)
        self.assertNotIn(99, terr.intruders)

    def test_animal_social_component(self):
        social = AnimalSocialComponent(group_id=1, group_role="leader")
        social.update_relationship(2, 0.5)
        self.assertAlmostEqual(social.get_relationship(2), 0.5)
        social.update_relationship(2, 0.6)
        self.assertAlmostEqual(social.get_relationship(2), 1.0)


class TestAnimalSystems(unittest.TestCase):
    """测试动物系统"""

    def setUp(self):
        self.world = World()

    def test_animal_memory_system(self):
        """测试记忆系统衰减"""
        from animal.systems.animal_memory_system import AnimalMemorySystem
        entity = self.world.create_entity()
        memory = AnimalMemoryComponent(decay_rate=0.5)
        AnimalMemorySystem.add_memory(memory, 1.0, 2.0, "food", value=0.8, timestamp=0)

        self.world.add_component(entity, AnimalComponent())
        self.world.add_component(entity, memory)
        self.world.add_component(entity, SpaceComponent(x=0, y=0))

        system = AnimalMemorySystem()
        system.update(self.world, dt=1.0)

        # 记忆应衰减
        self.assertLess(memory.memories[0].strength, 1.0)

    def test_animal_reproduction_system(self):
        """测试繁殖系统静态方法"""
        repro = AnimalReproductionComponent()
        
        # 测试冷却期
        self.assertTrue(AnimalReproductionSystem.is_ready(repro, 0))
        AnimalReproductionSystem.record_reproduction(repro, 10)
        self.assertFalse(AnimalReproductionSystem.is_ready(repro, 10))
        self.assertTrue(AnimalReproductionSystem.is_ready(repro, 35))
        
        # 测试怀孕
        AnimalReproductionSystem.start_pregnancy(repro, 50, mate_id=99)
        self.assertTrue(repro.is_pregnant)
        self.assertFalse(AnimalReproductionSystem.check_birth_ready(repro, 80))
        self.assertTrue(AnimalReproductionSystem.check_birth_ready(repro, 110))
        
        AnimalReproductionSystem.give_birth(repro)
        self.assertFalse(repro.is_pregnant)


if __name__ == "__main__":
    unittest.main()
