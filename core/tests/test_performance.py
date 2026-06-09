#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能基准测试

测试 ECS 核心性能：
1. 实体创建/销毁
2. 组件添加/查询
3. 系统更新
4. 空间查询（对比暴力 vs 索引）
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import time
import unittest

from core.world import World
from core.entity import Entity
from core.spatial_index import SpatialIndex

from space.space_component import SpaceComponent


class TestEntityPerformance(unittest.TestCase):
    """测试实体操作性能"""

    def test_bulk_entity_creation(self):
        """批量创建实体性能"""
        world = World()
        count = 10000

        start = time.time()
        for i in range(count):
            entity = world.create_entity()
            world.add_component(entity, SpaceComponent(x=i % 100, y=i // 100))
        elapsed = time.time() - start

        rate = count / elapsed
        print(f"\n  创建 {count} 实体: {elapsed:.3f}s ({rate:.0f}/s)")
        self.assertLess(elapsed, 5.0)

    def test_component_query_performance(self):
        """组件查询性能"""
        world = World()

        # 创建 1000 个带 SpaceComponent 的实体
        for i in range(1000):
            entity = world.create_entity()
            world.add_component(entity, SpaceComponent(x=i, y=i))

        # 查询 1000 次
        count = 1000
        start = time.time()
        for _ in range(count):
            list(world.get_components(SpaceComponent))
        elapsed = time.time() - start

        rate = count / elapsed
        print(f"\n  查询 {count} 次: {elapsed:.3f}s ({rate:.0f}/s)")
        self.assertLess(elapsed, 1.0)


class TestSpatialQueryPerformance(unittest.TestCase):
    """测试空间查询性能"""

    def test_brute_force_vs_index(self):
        """对比暴力查询和空间索引"""
        # 创建 5000 个实体
        entities = []
        positions = {}
        for i in range(5000):
            x = (i % 100) * 10
            y = (i // 100) * 10
            entities.append(i)
            positions[i] = (x, y)

        # 暴力查询
        def brute_force_query(center_x, center_y, radius):
            result = []
            r_sq = radius * radius
            for eid, (x, y) in positions.items():
                dx = x - center_x
                dy = y - center_y
                if dx * dx + dy * dy <= r_sq:
                    result.append(eid)
            return result

        # 空间索引
        index = SpatialIndex(cell_size=50.0)
        for eid, (x, y) in positions.items():
            index.add_entity(eid, x, y)

        # 对比查询性能
        query_count = 100

        # 暴力查询
        start = time.time()
        for _ in range(query_count):
            brute_force_query(500, 500, 100)
        brute_time = time.time() - start

        # 索引查询
        start = time.time()
        for _ in range(query_count):
            index.query_radius(500, 500, 100)
        index_time = time.time() - start

        print(f"\n  暴力查询: {brute_time:.3f}s")
        print(f"  索引查询: {index_time:.3f}s")
        if index_time > 0:
            print(f"  加速比: {brute_time / index_time:.1f}x")

        # 索引应至少快 5 倍
        self.assertLess(index_time, brute_time / 5)


class TestSystemUpdatePerformance(unittest.TestCase):
    """测试系统更新性能"""

    def test_system_update_bulk(self):
        """批量系统更新性能"""
        world = World()

        # 创建简单系统
        class SimpleSystem:
            tick_interval = 1
            def update(self, world, dt):
                for entity, space in world.get_components(SpaceComponent):
                    pass

        world.add_system(SimpleSystem())

        # 创建 1000 个实体
        for i in range(1000):
            entity = world.create_entity()
            world.add_component(entity, SpaceComponent(x=i, y=i))

        # 更新 100 帧
        count = 100
        start = time.time()
        for _ in range(count):
            world.update(dt=1.0)
        elapsed = time.time() - start

        fps = count / elapsed if elapsed > 0 else float('inf')
        print(f"\n  {count} 帧更新: {elapsed:.3f}s ({fps:.0f} fps)")
        self.assertLess(elapsed, 5.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
