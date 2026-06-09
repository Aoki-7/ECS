#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
碰撞检测系统测试

v3.0.1
"""

import unittest

from core.world import World
from space.space_component import SpaceComponent
from space.collision_system import (
    ColliderComponent, ObstacleComponent, CollisionSystem
)


class TestColliderComponent(unittest.TestCase):
    def test_defaults(self):
        c = ColliderComponent()
        self.assertEqual(c.radius, 0.5)
        self.assertTrue(c.is_solid)
        self.assertEqual(c.layer, 0)


class TestObstacleComponent(unittest.TestCase):
    def test_defaults(self):
        o = ObstacleComponent()
        self.assertEqual(o.obstacle_type, "wall")
        self.assertTrue(o.blocks_movement)


class TestCollisionSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.system = CollisionSystem(auto_resolve=True)
        self.world.add_system(self.system)

    def test_no_collision(self):
        """无碰撞场景"""
        e1 = self.world.create_entity()
        self.world.add_component(e1, SpaceComponent(x=0, y=0))
        self.world.add_component(e1, ColliderComponent(radius=1.0))

        e2 = self.world.create_entity()
        self.world.add_component(e2, SpaceComponent(x=10, y=10))
        self.world.add_component(e2, ColliderComponent(radius=1.0))

        self.system.update(self.world)
        # 无异常即通过

    def test_collision_detected(self):
        """碰撞检测"""
        e1 = self.world.create_entity()
        self.world.add_component(e1, SpaceComponent(x=0, y=0))
        self.world.add_component(e1, ColliderComponent(radius=2.0))

        e2 = self.world.create_entity()
        self.world.add_component(e2, SpaceComponent(x=1, y=0))
        self.world.add_component(e2, ColliderComponent(radius=2.0))

        # 更新前记录位置
        space1 = self.world.get_component(e1, SpaceComponent)
        space2 = self.world.get_component(e2, SpaceComponent)
        old_x1, old_x2 = space1.x, space2.x

        self.system.update(self.world)

        # 自动分离后位置应改变
        self.assertTrue(space1.x != old_x1 or space2.x != old_x2)

    def test_is_walkable_empty(self):
        """空世界可通行"""
        result = self.system.is_walkable(self.world, 5, 5)
        self.assertTrue(result)

    def test_is_walkable_blocked(self):
        """有障碍物不可通行"""
        e = self.world.create_entity()
        self.world.add_component(e, SpaceComponent(x=5, y=5))
        self.world.add_component(e, ObstacleComponent(blocks_movement=True))

        result = self.system.is_walkable(self.world, 5, 5)
        self.assertFalse(result)

    def test_is_walkable_with_collider(self):
        """有碰撞体不可通行"""
        e = self.world.create_entity()
        self.world.add_component(e, SpaceComponent(x=5, y=5))
        self.world.add_component(e, ColliderComponent(radius=1.0, is_solid=True))

        result = self.system.is_walkable(self.world, 5, 5, mover_radius=0.5)
        self.assertFalse(result)

    def test_is_walkable_self_excluded(self):
        """排除自身后可通行"""
        e = self.world.create_entity()
        self.world.add_component(e, SpaceComponent(x=5, y=5))
        self.world.add_component(e, ColliderComponent(radius=1.0, is_solid=True))

        result = self.system.is_walkable(
            self.world, 5, 5, mover_entity=e.id, mover_radius=0.5
        )
        self.assertTrue(result)

    def test_check_collision_at(self):
        """检查位置碰撞"""
        e = self.world.create_entity()
        self.world.add_component(e, SpaceComponent(x=0, y=0))
        self.world.add_component(e, ColliderComponent(radius=2.0))

        result = self.system.check_collision_at(self.world, 1, 0, radius=1.0)
        self.assertTrue(result)

        result = self.system.check_collision_at(self.world, 10, 10, radius=1.0)
        self.assertFalse(result)

    def test_layer_mask(self):
        """碰撞层掩码"""
        e1 = self.world.create_entity()
        self.world.add_component(e1, SpaceComponent(x=0, y=0))
        self.world.add_component(e1, ColliderComponent(radius=2.0, layer=0, mask=0x1))

        e2 = self.world.create_entity()
        self.world.add_component(e2, SpaceComponent(x=1, y=0))
        self.world.add_component(e2, ColliderComponent(radius=2.0, layer=1, mask=0x2))

        # 层掩码不匹配，不应碰撞
        self.system.update(self.world)
        # 无分离发生
        space1 = self.world.get_component(e1, SpaceComponent)
        space2 = self.world.get_component(e2, SpaceComponent)
        self.assertEqual(space1.x, 0)
        self.assertEqual(space2.x, 1)

    def test_obstacle_blocks(self):
        """障碍物阻挡移动实体"""
        # 移动实体
        mover = self.world.create_entity()
        self.world.add_component(mover, SpaceComponent(x=0, y=0))
        self.world.add_component(mover, ColliderComponent(radius=1.0))

        # 静态障碍物
        obs = self.world.create_entity()
        self.world.add_component(obs, SpaceComponent(x=0, y=0))
        self.world.add_component(obs, ColliderComponent(radius=1.0))
        self.world.add_component(obs, ObstacleComponent(blocks_movement=True))

        self.system.update(self.world)

        # 移动实体应被推开，障碍物不动
        mover_space = self.world.get_component(mover, SpaceComponent)
        obs_space = self.world.get_component(obs, SpaceComponent)
        self.assertNotEqual((mover_space.x, mover_space.y), (0, 0))
        self.assertEqual((obs_space.x, obs_space.y), (0, 0))


if __name__ == "__main__":
    unittest.main()
