#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建筑系统测试

v3.0.1
"""

import unittest

from core.world import World
from space.space_component import SpaceComponent
from space.collision_system import ColliderComponent, ObstacleComponent
from civilization.components.building_component import (
    BuildingComponent, BuildingInventoryComponent
)
from civilization.systems.building_system import BuildingSystem
from civilization.building_factory import BuildingFactory


class TestBuildingComponent(unittest.TestCase):
    def test_defaults(self):
        b = BuildingComponent()
        self.assertEqual(b.building_type, "hut")
        self.assertEqual(b.durability, 100.0)
        self.assertTrue(b.is_active)

    def test_take_damage(self):
        b = BuildingComponent(durability=100.0)
        BuildingSystem.take_damage(b, 30.0)
        self.assertEqual(b.durability, 70.0)
        self.assertTrue(b.is_active)

    def test_destroy(self):
        b = BuildingComponent(durability=50.0)
        BuildingSystem.take_damage(b, 50.0)
        self.assertEqual(b.durability, 0.0)
        self.assertFalse(b.is_active)

    def test_repair(self):
        b = BuildingComponent(durability=50.0, max_durability=100.0)
        BuildingSystem.take_damage(b, 30.0)
        BuildingSystem.repair(b, 20.0)
        self.assertEqual(b.durability, 40.0)
        self.assertTrue(b.is_active)

    def test_occupants(self):
        b = BuildingComponent(capacity=2)
        self.assertTrue(BuildingSystem.add_occupant(b, 1))
        self.assertTrue(BuildingSystem.add_occupant(b, 2))
        self.assertFalse(BuildingSystem.add_occupant(b, 3))  # 超出容量
        BuildingSystem.remove_occupant(b, 1)
        self.assertEqual(len(b.occupants), 1)


class TestBuildingInventory(unittest.TestCase):
    def test_add_remove(self):
        inv = BuildingInventoryComponent()
        self.assertTrue(BuildingSystem.add_item(inv, 101, 5.0))
        self.assertEqual(inv.items[101], 5.0)
        removed = BuildingSystem.remove_item(inv, 101, 2.0)
        self.assertEqual(removed, 2.0)
        self.assertEqual(inv.items[101], 3.0)

    def test_capacity_limit(self):
        inv = BuildingInventoryComponent(max_items=2)
        BuildingSystem.add_item(inv, 1)
        BuildingSystem.add_item(inv, 2)
        self.assertFalse(BuildingSystem.add_item(inv, 3))  # 超出容量


class TestBuildingFactory(unittest.TestCase):
    def setUp(self):
        self.world = World()

    def test_create_hut(self):
        entity = BuildingFactory.create_hut(self.world, x=10, y=20, owner_id=5)
        self.assertIsNotNone(entity)

        space = self.world.get_component(entity, SpaceComponent)
        self.assertEqual((space.x, space.y), (10, 20))

        building = self.world.get_component(entity, BuildingComponent)
        self.assertEqual(building.building_type, "hut")
        self.assertEqual(building.owner_id, 5)
        self.assertEqual(building.capacity, 4)

        # 检查碰撞体
        collider = self.world.get_component(entity, ColliderComponent)
        self.assertIsNotNone(collider)
        self.assertTrue(collider.is_solid)

        # 检查障碍物
        obstacle = self.world.get_component(entity, ObstacleComponent)
        self.assertIsNotNone(obstacle)
        self.assertTrue(obstacle.blocks_movement)

    def test_create_farm_no_block(self):
        """农场不阻挡移动"""
        entity = BuildingFactory.create_farm(self.world, x=5, y=5)

        obstacle = self.world.get_component(entity, ObstacleComponent)
        self.assertIsNone(obstacle)  # 农场不应有 ObstacleComponent

    def test_create_storage_with_inventory(self):
        """仓库有库存组件"""
        entity = BuildingFactory.create_storage(self.world, x=0, y=0)

        inv = self.world.get_component(entity, BuildingInventoryComponent)
        self.assertIsNotNone(inv)
        self.assertEqual(inv.max_items, 50)

    def test_building_presets(self):
        """测试所有预设类型"""
        for btype in ["hut", "workshop", "storage", "farm"]:
            entity = BuildingFactory.create_building(
                self.world, btype, x=0, y=0
            )
            building = self.world.get_component(entity, BuildingComponent)
            self.assertEqual(building.building_type, btype)

    def test_collision_system_integration(self):
        """建筑与碰撞系统集成"""
        from space.collision_system import CollisionSystem

        collision = CollisionSystem()
        self.world.add_system(collision)

        # 创建建筑
        BuildingFactory.create_hut(self.world, x=0, y=0)

        # 建筑位置应不可通行
        result = collision.is_walkable(self.world, 0, 0)
        self.assertFalse(result)

        # 远处应可通行
        result = collision.is_walkable(self.world, 10, 10)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
