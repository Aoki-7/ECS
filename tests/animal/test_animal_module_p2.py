#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物模块测试 v2 — 适配 Component 纯数据化

v3.9 适配：AnimalLearningComponent 方法迁移到 AnimalLearningSystem
"""

import unittest
from core.world import World
from animal.components.animal_component import AnimalComponent
from animal.components.animal_learning_component import AnimalLearningComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from animal.components.animal_perception_component import AnimalPerceptionComponent
from animal.components.animal_memory_component import AnimalMemoryComponent
from animal.systems.animal_learning_system import AnimalLearningSystem
from space.space_component import SpaceComponent


class TestLearningComponent(unittest.TestCase):
    """测试学习组件"""

    def test_record_behavior(self):
        """测试行为记录"""
        learn = AnimalLearningComponent()
        AnimalLearningSystem.record_behavior(learn, "graze", "food_rich", 0.8)
        AnimalLearningSystem.record_behavior(learn, "graze", "food_rich", 0.9)

        # 两次记录应合并
        self.assertEqual(len(learn.behavior_records), 1)
        self.assertAlmostEqual(AnimalLearningSystem.get_behavior_value(learn, "graze", "food_rich"), 0.85, places=1)

    def test_best_behavior(self):
        learn = AnimalLearningComponent()
        AnimalLearningSystem.record_behavior(learn, "graze", "food_rich", 0.8)
        AnimalLearningSystem.record_behavior(learn, "flee", "near_predator", 0.9)
        AnimalLearningSystem.record_behavior(learn, "explore", "neutral", 0.3)

        best = AnimalLearningSystem.get_best_behavior(learn, "food_rich")
        self.assertEqual(best, "graze")

        best_threat = AnimalLearningSystem.get_best_behavior(learn, "near_predator")
        self.assertEqual(best_threat, "flee")

    def test_habituation(self):
        learn = AnimalLearningComponent()
        AnimalLearningSystem.update_habituation(learn, "plant", 10)
        h1 = learn.habituation["plant"]
        AnimalLearningSystem.update_habituation(learn, "plant", 50)
        h2 = learn.habituation["plant"]

        # 习惯化应随暴露次数增加
        self.assertGreater(h2, h1)
        self.assertLess(h2, 1.0)

    def test_sensitization(self):
        learn = AnimalLearningComponent(learning_rate=0.5)
        AnimalLearningSystem.update_sensitization(learn, "predator", 1.0)
        s1 = learn.sensitization["predator"]
        AnimalLearningSystem.update_sensitization(learn, "predator", 1.0)
        s2 = learn.sensitization["predator"]

        self.assertEqual(s2, 1.0)  # 上限 1.0


class TestPerceptionSystem(unittest.TestCase):
    """测试感知系统"""

    def setUp(self):
        self.world = World()

    def test_perception_update(self):
        """测试感知更新"""
        entity = self.world.create_entity()
        animal = AnimalComponent()
        perception = AnimalPerceptionComponent()
        needs = AnimalNeedsComponent()
        space = SpaceComponent(x=10, y=10)

        self.world.add_component(entity, animal)
        self.world.add_component(entity, perception)
        self.world.add_component(entity, needs)
        self.world.add_component(entity, space)

        # 创建目标实体
        target = self.world.create_entity()
        target_space = SpaceComponent(x=15, y=10)
        self.world.add_component(target, target_space)

        # 手动添加检测
        perception.add_detection(target.id, "plant")
        self.assertTrue(perception.has_detected(target.id))

    def test_detection_types(self):
        """测试按类型检测"""
        perception = AnimalPerceptionComponent()
        perception.add_detection(1, "plant")
        perception.add_detection(2, "predator")
        perception.add_detection(3, "plant")

        plants = perception.get_by_type("plant")
        self.assertEqual(len(plants), 2)

        predators = perception.get_by_type("predator")
        self.assertEqual(len(predators), 1)


class TestMemoryComponent(unittest.TestCase):
    """测试记忆组件"""

    def test_memory_storage(self):
        """测试记忆存储"""
        from animal.systems.animal_memory_system import AnimalMemorySystem
        memory = AnimalMemoryComponent()
        AnimalMemorySystem.add_memory(memory, 1.0, 2.0, "danger", value=0.8, timestamp=0)

        self.assertEqual(len(memory.memories), 1)

    def test_memory_decay(self):
        """测试记忆衰减"""
        from animal.systems.animal_memory_system import AnimalMemorySystem
        memory = AnimalMemoryComponent()
        AnimalMemorySystem.add_memory(memory, 1.0, 2.0, "danger", value=0.8, timestamp=0)
        AnimalMemorySystem.decay(memory)

        # 衰减后记忆应该还在但强度降低
        self.assertGreater(len(memory.memories), 0)
        self.assertLess(memory.memories[0].strength, 1.0)


class TestNeedsSystem(unittest.TestCase):
    """测试需求系统"""

    def test_hunger_increase(self):
        """测试饥饿度增加"""
        needs = AnimalNeedsComponent()
        initial_hunger = needs.hunger

        # 模拟时间流逝
        needs.hunger = min(1.0, needs.hunger + 0.1)
        self.assertGreater(needs.hunger, initial_hunger)

    def test_critical_needs(self):
        """测试临界需求"""
        needs = AnimalNeedsComponent()
        needs.hunger = 0.9
        needs.thirst = 0.9
        needs.fear = 0.9

        # 应该返回最紧急的需求
        dominant = needs.get_dominant_need()
        self.assertIn(dominant, ["hunger", "thirst", "fear"])


class TestAnimalComponent(unittest.TestCase):
    """测试动物组件"""

    def test_gender_assignment(self):
        """测试性别分配"""
        animal = AnimalComponent()
        self.assertIn(animal.gender, ["male", "female"])

    def test_age_progression(self):
        """测试年龄增长"""
        animal = AnimalComponent()
        initial_age = animal.age
        animal.age += 1
        self.assertEqual(animal.age, initial_age + 1)


if __name__ == "__main__":
    unittest.main()
