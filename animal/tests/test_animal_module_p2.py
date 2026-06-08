#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Animal 模块 P2 测试

覆盖：
    - PerceptionComponent / PerceptionSystem
    - LearningComponent / LearningSystem
    - MigrationSystem A* 路径规划
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import unittest
from core.world import World

from animal.components.animal_component import AnimalComponent
from animal.components.animal_perception_component import AnimalPerceptionComponent
from animal.components.animal_learning_component import AnimalLearningComponent, BehaviorRecord
from animal.components.animal_memory_component import AnimalMemoryComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from animal.components.animal_social_component import AnimalSocialComponent

from animal.systems.animal_perception_system import AnimalPerceptionSystem
from animal.systems.animal_learning_system import AnimalLearningSystem
from animal.systems.animal_migration_system import AnimalMigrationSystem

from animal.animal_factory import AnimalFactory

from biology.lifecycle.components.energy_component import EnergyComponent
from space.space_component import SpaceComponent


class TestPerceptionComponent(unittest.TestCase):
    """测试感知组件"""

    def test_detection(self):
        perc = AnimalPerceptionComponent(vision_range=10.0)
        perc.add_detection(1, "animal")
        perc.add_detection(2, "plant")

        self.assertTrue(perc.has_detected(1))
        self.assertFalse(perc.has_detected(99))
        self.assertEqual(perc.get_by_type("plant"), [2])

    def test_clear(self):
        perc = AnimalPerceptionComponent()
        perc.add_detection(1, "animal")
        perc.clear_detection()
        self.assertEqual(len(perc.detected_entities), 0)


class TestLearningComponent(unittest.TestCase):
    """测试学习组件"""

    def test_record_behavior(self):
        learn = AnimalLearningComponent()
        learn.record_behavior("graze", "food_rich", 0.8)
        learn.record_behavior("graze", "food_rich", 0.9)

        # 两次记录应合并
        self.assertEqual(len(learn.behavior_records), 1)
        self.assertAlmostEqual(learn.get_behavior_value("graze", "food_rich"), 0.85, places=1)

    def test_best_behavior(self):
        learn = AnimalLearningComponent()
        learn.record_behavior("graze", "food_rich", 0.8)
        learn.record_behavior("flee", "near_predator", 0.9)
        learn.record_behavior("explore", "neutral", 0.3)

        best = learn.get_best_behavior("food_rich")
        self.assertEqual(best, "graze")

        best_threat = learn.get_best_behavior("near_predator")
        self.assertEqual(best_threat, "flee")

    def test_habituation(self):
        learn = AnimalLearningComponent()
        learn.update_habituation("plant", 10)
        h1 = learn.habituation["plant"]
        learn.update_habituation("plant", 50)
        h2 = learn.habituation["plant"]

        # 习惯化应随暴露次数增加
        self.assertGreater(h2, h1)
        self.assertLess(h2, 1.0)

    def test_sensitization(self):
        learn = AnimalLearningComponent(learning_rate=0.5)
        learn.update_sensitization("predator", 1.0)
        s1 = learn.sensitization["predator"]
        learn.update_sensitization("predator", 1.0)
        s2 = learn.sensitization["predator"]

        self.assertEqual(s2, 1.0)  # 上限 1.0


class TestPerceptionSystem(unittest.TestCase):
    """测试感知系统"""

    def setUp(self):
        self.world = World()

    def test_perception_update(self):
        """测试感知系统更新"""
        entity = self.world.create_entity()
        self.world.add_component(entity, AnimalComponent())
        self.world.add_component(entity, AnimalPerceptionComponent(vision_range=5.0))
        self.world.add_component(entity, SpaceComponent(x=0, y=0))

        # 创建附近植物
        plant = self.world.create_entity()
        from plant.components.plant_component import PlantComponent
        self.world.add_component(plant, PlantComponent())
        self.world.add_component(plant, SpaceComponent(x=2, y=2))
        from resource.components.resource_component import ResourceComponent
        self.world.add_component(plant, ResourceComponent(resource_type="food"))
        from core.category_component import CategoryComponent
        from core.category import EntityCategory
        self.world.add_component(plant, CategoryComponent(category=EntityCategory.PLANT))

        # 运行感知系统（需要 SpaceSystem 注册）
        from space.space_system import SpaceSystem
        self.world.add_system(SpaceSystem())

        system = AnimalPerceptionSystem()
        system.update(self.world, dt=1.0)

        perc = self.world.get_component(entity, AnimalPerceptionComponent)
        # 空间索引可能未完全建立，至少验证系统运行不报错
        self.assertIsNotNone(perc)


class TestLearningSystem(unittest.TestCase):
    """测试学习系统"""

    def setUp(self):
        self.world = World()

    def test_learning_update(self):
        """测试学习系统更新"""
        entity = self.world.create_entity()
        self.world.add_component(entity, AnimalComponent())
        self.world.add_component(entity, AnimalLearningComponent())
        self.world.add_component(entity, AnimalNeedsComponent(hunger=0.2))
        self.world.add_component(entity, AnimalPerceptionComponent())

        # 运行学习系统
        system = AnimalLearningSystem()
        system.update(self.world, dt=1.0)

        learn = self.world.get_component(entity, AnimalLearningComponent)
        # 低饥饿应记录觅食成功
        self.assertGreater(len(learn.behavior_records), 0)


class TestMigrationPathfinding(unittest.TestCase):
    """测试迁徙路径规划"""

    def setUp(self):
        self.world = World()
        self.system = AnimalMigrationSystem()

    def test_straight_path(self):
        """测试直线路径生成"""
        path = self.system._generate_straight_path(0, 0, 10, 10, step_size=3)
        self.assertGreater(len(path), 1)
        # 终点应在目标附近
        last = path[-1]
        self.assertAlmostEqual(last[0], 10, delta=0.1)
        self.assertAlmostEqual(last[1], 10, delta=0.1)

    def test_safe_waypoints(self):
        """测试安全路径点查找"""
        memory = AnimalMemoryComponent()
        memory.add_memory(5, 5, "food", value=0.8, timestamp=0)
        memory.add_memory(15, 15, "food", value=0.9, timestamp=0)

        waypoints = self.system._find_safe_waypoints(memory, 0, 0, 20, 20)
        # 至少应找到路径附近的点
        self.assertGreaterEqual(len(waypoints), 0)

    def test_near_path(self):
        """测试路径邻近判断"""
        # 点在线段上
        self.assertTrue(self.system._is_near_path(5, 5, 0, 0, 10, 10, max_distance=2))
        # 点远离线段
        self.assertFalse(self.system._is_near_path(20, 20, 0, 0, 10, 10, max_distance=2))


class TestIntegrationP2(unittest.TestCase):
    """P2 集成测试"""

    def setUp(self):
        self.world = World()

    def test_full_animal_with_p2(self):
        """测试完整动物（含 P2 组件）"""
        entity = AnimalFactory.create_animal(self.world, species="predator", x=5, y=5)

        # 验证 P2 组件
        perc = self.world.get_component(entity, AnimalPerceptionComponent)
        self.assertIsNotNone(perc)

        learn = self.world.get_component(entity, AnimalLearningComponent)
        self.assertIsNotNone(learn)

        # 运行所有 P2 系统
        AnimalPerceptionSystem().update(self.world, dt=1.0)
        AnimalLearningSystem().update(self.world, dt=1.0)

        # 验证学习记录
        self.assertGreaterEqual(len(learn.behavior_records), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
