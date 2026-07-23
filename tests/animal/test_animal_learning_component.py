#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物学习组件测试

v3.9 适配：Component 纯数据化，方法迁移到 AnimalLearningSystem
"""

import unittest
from biology.organisms.animal.components.animal_learning_component import AnimalLearningComponent
from biology.organisms.animal.systems.animal_learning_system import AnimalLearningSystem


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


if __name__ == "__main__":
    unittest.main()