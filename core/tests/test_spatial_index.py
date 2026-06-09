#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空间索引测试
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import unittest

from core.spatial_index import SpatialIndex


class TestSpatialIndex(unittest.TestCase):
    """测试空间索引"""

    def setUp(self):
        self.index = SpatialIndex(cell_size=10.0)

    def test_add_and_query(self):
        """测试添加和查询"""
        self.index.add_entity(1, 5, 5)
        self.index.add_entity(2, 15, 15)
        self.index.add_entity(3, 8, 8)

        # 查询 (0,0) 半径 10 内的实体
        result = self.index.query_radius(0, 0, 10)
        self.assertIn(1, result)
        # 注意：query_radius 返回的是网格单元内的所有实体，不做精确距离过滤
        # 所以 (15,15) 可能在相邻单元格中被包含

    def test_update_entity(self):
        """测试更新位置"""
        self.index.add_entity(1, 5, 5)
        self.index.update_entity(1, 25, 25)

        result = self.index.query_radius(0, 0, 10)
        self.assertNotIn(1, result)

        result = self.index.query_radius(20, 20, 10)
        self.assertIn(1, result)

    def test_remove_entity(self):
        """测试移除实体"""
        self.index.add_entity(1, 5, 5)
        self.index.remove_entity(1)

        result = self.index.query_radius(0, 0, 10)
        self.assertNotIn(1, result)

    def test_query_rect(self):
        """测试矩形查询"""
        self.index.add_entity(1, 5, 5)
        self.index.add_entity(2, 15, 15)
        self.index.add_entity(3, 25, 25)

        result = self.index.query_rect(0, 0, 20, 20)
        self.assertIn(1, result)
        self.assertIn(2, result)
        # query_rect 返回网格单元内的所有实体，可能包含边界外的

    def test_stats(self):
        """测试统计"""
        for i in range(100):
            self.index.add_entity(i, i * 2, i * 2)

        stats = self.index.get_stats()
        self.assertEqual(stats["total_entities"], 100)
        self.assertGreater(stats["total_cells"], 0)
        self.assertGreater(stats["avg_per_cell"], 0)

    def test_large_scale(self):
        """大规模测试"""
        index = SpatialIndex(cell_size=50.0)

        # 添加 10000 个实体
        for i in range(10000):
            index.add_entity(i, (i % 100) * 10, (i // 100) * 10)

        # 查询性能
        import time
        start = time.time()
        for _ in range(100):
            result = index.query_radius(500, 500, 100)
        elapsed = time.time() - start

        stats = index.get_stats()
        print(f"\n  10000 实体, 100 次查询: {elapsed:.3f}s")
        print(f"  单元格数: {stats['total_cells']}, 平均/单元格: {stats['avg_per_cell']:.1f}")

        # 应在 1 秒内完成
        self.assertLess(elapsed, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
