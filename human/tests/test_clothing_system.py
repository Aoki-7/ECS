#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
衣物系统测试

v3.0.1
"""

import unittest

from core.world import World
from human.components.clothing_component import ClothingComponent, OutfitComponent
from human.systems.clothing_system import ClothingSystem
from biology.components.physiology_needs_component import PhysiologyNeedsComponent


class TestClothingComponent(unittest.TestCase):
    def test_insulation(self):
        clothing = ClothingComponent(insulation=10.0, durability=1.0)
        self.assertEqual(clothing.calculate_effective_insulation(), 10.0)

    def test_wetness_reduces_insulation(self):
        clothing = ClothingComponent(insulation=10.0, wetness=0.5)
        effective = clothing.calculate_effective_insulation()
        self.assertLess(effective, 10.0)

    def test_wear(self):
        clothing = ClothingComponent(durability=1.0)
        clothing.wear(0.1)
        self.assertEqual(clothing.durability, 0.9)
        self.assertEqual(clothing.condition, "good")

    def test_wear_to_ruined(self):
        clothing = ClothingComponent(durability=0.15)
        clothing.wear(0.1)
        self.assertEqual(clothing.condition, "ruined")

    def test_repair(self):
        clothing = ClothingComponent(durability=0.3)
        clothing.repair(0.3)
        self.assertEqual(clothing.durability, 0.6)
        self.assertEqual(clothing.condition, "worn")


class TestOutfitComponent(unittest.TestCase):
    def test_wear_remove(self):
        outfit = OutfitComponent()
        outfit.wear_item(1, ClothingComponent(clothing_type="tunic"))
        self.assertIn("tunic", outfit.worn_items)

        removed = outfit.remove_item("tunic")
        self.assertEqual(removed, 1)
        self.assertNotIn("tunic", outfit.worn_items)


class TestClothingSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.system = ClothingSystem()

    def test_temperature_adaptation(self):
        """温度适应"""
        needs = PhysiologyNeedsComponent(energy=100.0)
        outfit = OutfitComponent()

        # 寒冷环境，无衣物
        self.system._apply_temperature_effects(1, needs, 5.0, 0.0)
        self.assertLess(needs.energy, 100.0)

        # 重置，有保暖衣物
        needs.energy = 100.0
        self.system._apply_temperature_effects(1, needs, 5.0, 15.0)
        # 有效温度 = 5 + 15 = 20，在舒适范围内
        self.assertEqual(needs.energy, 100.0)


if __name__ == "__main__":
    unittest.main()
