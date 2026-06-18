#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
农场系统测试

v3.0.1
"""

import unittest

from core.world import World
from space.space_component import SpaceComponent
from environment.soil.components.soil_component import SoilComponent
from civilization.components.farm_component import (
    FarmPlotComponent, FarmingKnowledgeComponent, IrrigationComponent
)
from civilization.systems.farm_system import FarmSystem, HarvestSystem, FarmPlotSystem, FarmingKnowledgeSystem, IrrigationSystem


class TestFarmPlotComponent(unittest.TestCase):
    def test_defaults(self):
        farm = FarmPlotComponent()
        self.assertEqual(farm.soil_quality, 0.5)
        self.assertIsNone(farm.crop_type)
        self.assertEqual(farm.growth_stage, 0.0)

    def test_can_harvest(self):
        farm = FarmPlotComponent(crop_type="wheat", growth_stage=0.95)
        self.assertTrue(FarmPlotSystem.can_harvest(farm))

        farm.growth_stage = 0.5
        self.assertFalse(FarmPlotSystem.can_harvest(farm))

    def test_calculate_yield(self):
        farm = FarmPlotComponent(
            crop_type="wheat", soil_quality=0.8,
            growth_stage=0.9
        )
        yield_amount = FarmPlotSystem.calculate_yield(farm)
        self.assertGreater(yield_amount, 0.0)
        self.assertLessEqual(yield_amount, 1.0)

    def test_update_growth(self):
        farm = FarmPlotComponent(crop_type="wheat", growth_stage=0.0)
        conditions = {"temperature": 22.0, "light": 0.7, "moisture": 0.5}

        FarmPlotSystem.update_growth(farm, 10.0, conditions)
        self.assertGreater(farm.growth_stage, 0.0)
        self.assertLess(farm.growth_stage, 1.0)

    def test_water_stress(self):
        """水分胁迫影响生长"""
        farm = FarmPlotComponent(
            crop_type="wheat", moisture=0.05
        )
        conditions = {"temperature": 22.0, "light": 0.7, "moisture": 0.5}

        FarmPlotSystem.update_growth(farm, 10.0, conditions)
        self.assertLess(farm.moisture, 1.0)


class TestFarmingKnowledge(unittest.TestCase):
    def test_record_planting(self):
        fk = FarmingKnowledgeComponent()
        FarmingKnowledgeSystem.record_planting(
            fk,
            crop_type="wheat", soil_type="loam", season="spring",
            yield_amount=0.8, success=True,
        )

        self.assertIn("wheat", fk.planting_techniques)
        self.assertGreater(fk.planting_techniques["wheat"], 0.0)

    def test_best_crop_selection(self):
        fk = FarmingKnowledgeComponent()
        fk.known_crops = ["wheat", "corn"]

        best = FarmingKnowledgeSystem.get_best_crop_for_conditions(fk, "loam", "spring")
        self.assertEqual(best, "wheat")

    def test_irrigation_learning(self):
        fk = FarmingKnowledgeComponent()
        level = FarmingKnowledgeSystem.suggest_irrigation_level(fk)
        self.assertEqual(level, 0.5)


class TestIrrigationComponent(unittest.TestCase):
    def test_irrigate(self):
        irrigation = IrrigationComponent(efficiency=0.8)
        farm = FarmPlotComponent(moisture=0.3)

        actual = IrrigationSystem.irrigate(irrigation, farm, 0.5)
        self.assertEqual(actual, 0.4)
        self.assertGreater(farm.moisture, 0.3)

    def test_irrigation_learning(self):
        fk = FarmingKnowledgeComponent()
        level = FarmingKnowledgeSystem.suggest_irrigation_level(fk)
        self.assertEqual(level, 0.5)


class TestIrrigationComponent(unittest.TestCase):
    def test_irrigate(self):
        irr = IrrigationComponent(flow_rate=0.2, efficiency=0.8)
        farm = FarmPlotComponent(moisture=0.2)

        actual = IrrigationSystem.irrigate(irr, farm, 0.3)
        self.assertAlmostEqual(actual, 0.24)  # 0.3 * 0.8
        self.assertAlmostEqual(farm.moisture, 0.44)  # 0.2 + 0.24


class TestFarmSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.system = FarmSystem()

    def test_soil_quality_calculation(self):
        """土壤质量计算"""
        soil = SoilComponent(ph=6.5, nitrogen=80, phosphorus=30, potassium=70,
                            organic_matter=3.0, moisture=0.5)
        quality = self.system._calculate_soil_quality(soil)
        self.assertGreater(quality, 0.0)
        self.assertLessEqual(quality, 1.0)

    def test_growth_update(self):
        """生长更新"""
        entity = self.world.create_entity()
        farm = FarmPlotComponent(crop_type="wheat", growth_stage=0.0)
        self.world.add_component(entity, farm)
        self.world.add_component(entity, SpaceComponent(x=0, y=0))

        self.system.update(self.world, dt=10.0)

        self.assertGreater(farm.growth_stage, 0.0)

    def test_season_detection(self):
        """季节检测"""
        self.assertEqual(self.system._get_season(50), "spring")
        self.assertEqual(self.system._get_season(120), "summer")
        self.assertEqual(self.system._get_season(200), "autumn")
        self.assertEqual(self.system._get_season(300), "winter")


class TestHarvestSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.system = HarvestSystem()

    def test_harvest_mature_crop(self):
        """收割成熟作物"""
        from human.components.action.action_component import ActionComponent, ActionType
        from human.components.cognitive.task_component import TaskComponent
        from human.components.economic.inventory.inventory_component import InventoryComponent

        # 创建农田
        farm_entity = self.world.create_entity()
        farm = FarmPlotComponent(crop_type="wheat", growth_stage=0.95)
        self.world.add_component(farm_entity, farm)
        self.world.add_component(farm_entity, SpaceComponent(x=0, y=0))

        # 创建收割者
        worker = self.world.create_entity()
        action = ActionComponent(current_action=ActionType.HARVEST)
        action.target_entity = farm_entity.id
        self.world.add_component(worker, action)
        self.world.add_component(worker, TaskComponent())
        self.world.add_component(worker, InventoryComponent())
        self.world.add_component(worker, FarmingKnowledgeComponent())

        # 执行收割
        self.system.update(self.world)

        # 检查农田已重置
        self.assertIsNone(farm.crop_type)
        self.assertEqual(farm.growth_stage, 0.0)

        # 检查记录了产量历史
        self.assertEqual(len(farm.yield_history), 1)

    def test_harvest_immature(self):
        """收割未成熟作物失败"""
        from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
        from human.components.cognitive.task_component import TaskComponent
        from human.components.economic.inventory.inventory_component import InventoryComponent

        farm_entity = self.world.create_entity()
        farm = FarmPlotComponent(crop_type="wheat", growth_stage=0.3)
        self.world.add_component(farm_entity, farm)
        self.world.add_component(farm_entity, SpaceComponent(x=0, y=0))

        worker = self.world.create_entity()
        action = ActionComponent(current_action=ActionType.HARVEST)
        action.target_entity = farm_entity.id
        self.world.add_component(worker, action)
        self.world.add_component(worker, TaskComponent())
        self.world.add_component(worker, InventoryComponent())

        self.system.update(self.world)

        # 未成熟作物不会被收割，状态保持不变
        self.assertEqual(farm.crop_type, "wheat")
        self.assertEqual(farm.growth_stage, 0.3)


if __name__ == "__main__":
    unittest.main()
