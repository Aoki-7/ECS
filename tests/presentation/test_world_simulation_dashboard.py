#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界模拟仪表盘测试

v3.0.1
"""

import os
import sys
import unittest

sys.path.insert(0, r"D:\个人助手\workspace\ECS")

from core.world import World
from presentation.visualization.world_simulation_dashboard import WorldSimulationDashboard


class TestWorldSimulationDashboard(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.dashboard = WorldSimulationDashboard(self.world)

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.dashboard)
        self.assertEqual(self.dashboard.world, self.world)

    def test_capture_snapshot(self):
        """测试捕获快照"""
        snapshot = self.dashboard.capture_snapshot()
        self.assertEqual(snapshot.tick, 0)
        self.assertEqual(snapshot.total_entities, 0)

    def test_get_entity_positions(self):
        """测试获取实体位置"""
        positions = self.dashboard.get_entity_positions()
        self.assertIsInstance(positions, list)

    def test_export_json_data(self):
        """测试导出 JSON 数据"""
        data = self.dashboard.export_json_data()
        self.assertIn("snapshot", data)
        self.assertIn("history", data)
        self.assertIn("entities", data)

    def test_export_html(self):
        """测试导出 HTML"""
        filepath = "test_world_dashboard.html"
        result = self.dashboard.export_html(filepath)
        self.assertTrue(os.path.exists(result))
        if os.path.exists(result):
            os.remove(result)


if __name__ == "__main__":
    unittest.main()