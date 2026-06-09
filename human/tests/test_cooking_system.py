#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烹饪系统测试

v3.0.1
"""

import unittest

from core.world import World
from human.systems.action.cooking_system import CookingSystem
from core.components.action_component import ActionComponent, ActionType, ActionStatus
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.economic.inventory.inventory_component import InventoryComponent


class TestCookingSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.system = CookingSystem()

    def test_cooking_result_raw(self):
        """未充分加热"""
        result = self.system._calculate_cooking_result(None, 20.0, 0.5, 0.0)
        self.assertEqual(result["state"], "raw")
        self.assertTrue(result["edible"])

    def test_cooking_result_cooked(self):
        """完美烹饪"""
        result = self.system._calculate_cooking_result(None, 100.0, 0.5, 0.5)
        self.assertEqual(result["state"], "cooked")
        self.assertTrue(result["edible"])
        self.assertGreater(result["quality"], 0.5)

    def test_cooking_result_overcooked(self):
        """过熟"""
        result = self.system._calculate_cooking_result(None, 200.0, 0.5, 0.5)
        self.assertEqual(result["state"], "overcooked")
        self.assertTrue(result["edible"])

    def test_cooking_result_burnt(self):
        """烧焦"""
        result = self.system._calculate_cooking_result(None, 200.0, 1.0, 0.5)
        self.assertEqual(result["state"], "burnt")
        self.assertFalse(result["edible"])

    def test_skill_improves_quality(self):
        """技能提升质量"""
        result_low = self.system._calculate_cooking_result(None, 80.0, 0.5, 0.0)
        result_high = self.system._calculate_cooking_result(None, 80.0, 0.5, 1.0)
        self.assertGreater(result_high["quality"], result_low["quality"])

    def test_cooking_process(self):
        """完整烹饪流程"""
        from civilization.components.crafting_knowledge_component import CraftingKnowledgeComponent

        worker = self.world.create_entity()
        action = ActionComponent(current_action=ActionType.EAT)
        action.target_entity = 999  # 虚拟原料
        self.world.add_component(worker, action)
        self.world.add_component(worker, TaskComponent())
        self.world.add_component(worker, InventoryComponent())

        self.system.update(self.world)

        # 检查是否记录了知识
        knowledge = self.world.get_component(worker, CraftingKnowledgeComponent)
        self.assertIsNotNone(knowledge)


if __name__ == "__main__":
    unittest.main()
