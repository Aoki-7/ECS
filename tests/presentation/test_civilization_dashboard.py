#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文明演化仪表盘测试

v3.0.1
"""

import os
import sys
import unittest

sys.path.insert(0, r"D:\个人助手\workspace\ECS")

from core.world import World
from presentation.visualization.civilization_dashboard import CivilizationDashboard


class TestCivilizationDashboard(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.dashboard = CivilizationDashboard(self.world)

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.dashboard)
        self.assertEqual(self.dashboard.world, self.world)

    def test_generate_dashboard_data(self):
        """测试生成仪表盘数据"""
        data = self.dashboard.generate_dashboard_data()
        self.assertIn("tick", data)
        self.assertIn("entities", data)
        self.assertIn("statistics", data)

    def test_export_html(self):
        """测试导出 HTML"""
        filepath = "test_dashboard.html"
        result = self.dashboard.export_html(filepath)
        self.assertTrue(os.path.exists(result))
        # 清理
        if os.path.exists(result):
            os.remove(result)


if __name__ == "__main__":
    unittest.main()
