#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径规划服务测试

v3.0.1
"""

import unittest

from space.pathfinding import PathNode, PathfindingService


class TestPathNode(unittest.TestCase):
    def test_equality(self):
        a = PathNode(1, 2)
        b = PathNode(1, 2)
        c = PathNode(2, 3)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_hash(self):
        a = PathNode(1, 2)
        b = PathNode(1, 2)
        self.assertEqual(hash(a), hash(b))


class TestPathfindingService(unittest.TestCase):
    def setUp(self):
        self.pf = PathfindingService(world_bounds=(0, 0, 20, 20))

    def test_find_path_straight(self):
        """直线路径"""
        path = self.pf.find_path(0, 0, 5, 0, lambda x, y: True)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (5, 0))

    def test_find_path_with_obstacle(self):
        """有障碍物的路径"""
        obstacles = {(2, 0), (2, 1), (2, -1)}
        path = self.pf.find_path(
            0, 0, 5, 0,
            lambda x, y: (x, y) not in obstacles
        )
        self.assertIsNotNone(path)
        # 路径应绕过 (2, *) 的障碍物
        for px, py in path:
            self.assertNotIn((px, py), obstacles)

    def test_find_path_unreachable(self):
        """不可达目标"""
        # 目标被墙包围
        is_walkable = lambda x, y: (x, y) != (5, 5)
        path = self.pf.find_path(0, 0, 5, 5, is_walkable)
        self.assertIsNone(path)

    def test_find_path_diagonal(self):
        """对角移动"""
        path = self.pf.find_path(0, 0, 3, 3, lambda x, y: True, allow_diagonal=True)
        self.assertIsNotNone(path)
        # 对角路径应更短
        self.assertLess(len(path), 6)

    def test_find_path_no_diagonal(self):
        """禁止对角移动"""
        path = self.pf.find_path(0, 0, 3, 3, lambda x, y: True, allow_diagonal=False)
        self.assertIsNotNone(path)
        # 只能走直角，路径更长
        self.assertGreaterEqual(len(path), 6)

    def test_line_of_sight_clear(self):
        """视线清晰"""
        result = self.pf.line_of_sight(0, 0, 5, 5, lambda x, y: True)
        self.assertTrue(result)

    def test_line_of_sight_blocked(self):
        """视线被阻挡"""
        obstacles = {(2, 2), (3, 3)}
        result = self.pf.line_of_sight(
            0, 0, 5, 5,
            lambda x, y: (x, y) not in obstacles
        )
        self.assertFalse(result)

    def test_smooth_path(self):
        """路径平滑"""
        path = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
        smoothed = self.pf.smooth_path(path, lambda x, y: True)
        self.assertEqual(smoothed[0], (0, 0))
        self.assertEqual(smoothed[-1], (5, 0))
        self.assertLessEqual(len(smoothed), len(path))

    def test_find_nearest_reachable(self):
        """查找最近可达点"""
        obstacles = {(5, 5)}
        result = self.pf.find_nearest_reachable(
            0, 0, 5, 5,
            lambda x, y: (x, y) not in obstacles,
            max_radius=3
        )
        self.assertIsNotNone(result)
        self.assertNotEqual(result, (5, 5))

    def test_flow_field(self):
        """流场生成"""
        flow = self.pf.generate_flow_field(
            5, 5,
            lambda x, y: True,
            width=10, height=10
        )
        self.assertGreater(len(flow), 0)
        # 起点应指向目标
        if (0, 0) in flow:
            dx, dy = flow[(0, 0)]
            self.assertTrue(dx >= 0 and dy >= 0)

    def test_same_start_goal(self):
        """起点终点相同"""
        path = self.pf.find_path(5, 5, 5, 5, lambda x, y: True)
        self.assertEqual(path, [(5, 5)])

    def test_out_of_bounds(self):
        """边界限制"""
        pf = PathfindingService(world_bounds=(0, 0, 5, 5))
        path = pf.find_path(0, 0, 10, 10, lambda x, y: True)
        self.assertIsNone(path)


if __name__ == "__main__":
    unittest.main()