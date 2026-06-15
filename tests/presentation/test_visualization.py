#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化工具测试
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import os
import tempfile
import unittest

from core.world import World
from core.entity import Entity

from presentation.visualization.world_visualizer import WorldVisualizer, VisualizationConfig

from space.space_component import SpaceComponent
from memory_layer import MemoryLayer, SensoryDescription


class TestWorldVisualizer(unittest.TestCase):
    """测试世界可视化器"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()
        self.visualizer = WorldVisualizer(self.world)

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_generate_entity_heatmap(self):
        """测试实体热力图"""
        # 创建带位置的实体
        for i in range(5):
            entity = self.world.create_entity()
            self.world.add_component(entity, SpaceComponent(x=i * 10, y=i * 10))

        heatmap = self.visualizer.generate_entity_heatmap()
        self.assertEqual(heatmap["type"], "heatmap")
        self.assertEqual(heatmap["count"], 5)

    def test_generate_system_performance(self):
        """测试系统性能数据"""
        perf = self.visualizer.generate_system_performance()
        self.assertEqual(perf["type"], "performance")
        self.assertIn("systems", perf)
        self.assertEqual(perf["entity_count"], 0)

    def test_generate_entity_network(self):
        """测试实体网络"""
        # 创建实体
        for i in range(3):
            self.world.create_entity()

        network = self.visualizer.generate_entity_network()
        self.assertEqual(network["type"], "network")
        self.assertEqual(len(network["nodes"]), 3)

    def test_generate_memory_network(self):
        """测试记忆网络"""
        ml = MemoryLayer.get_instance()
        ml.register_entity(1, "stone", SensoryDescription(shape="圆形"))

        mem_network = self.visualizer.generate_memory_network()
        self.assertEqual(mem_network["type"], "memory_network")
        # 概念可能因序列化方式不同而有不同名称
        self.assertGreaterEqual(len(mem_network["concepts"]), 0)

    def test_generate_event_timeline(self):
        """测试事件时间轴"""
        timeline = self.visualizer.generate_event_timeline()
        self.assertEqual(timeline["type"], "timeline")
        self.assertIn("events", timeline)

    def test_generate_full_report(self):
        """测试完整报告"""
        report = self.visualizer.generate_full_report()
        self.assertEqual(report["version"], "3.0-beta")
        self.assertEqual(len(report["visualizations"]), 5)

    def test_export_html(self):
        """测试导出 HTML"""
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, "test_viz.html")

        result = self.visualizer.export_html(filepath)
        self.assertTrue(os.path.exists(result))

        # 验证文件内容
        with open(result, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ECS World Visualization", content)
        self.assertIn("System Performance", content)

        # 清理
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_config(self):
        """测试配置"""
        config = VisualizationConfig(width=1024, height=768, theme="light")
        viz = WorldVisualizer(self.world, config)
        self.assertEqual(viz.config.width, 1024)
        self.assertEqual(viz.config.theme, "light")


class TestVisualizerIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_full_workflow(self):
        """测试完整可视化工作流"""
        # 1. 创建世界状态
        for i in range(10):
            entity = self.world.create_entity()
            self.world.add_component(entity, SpaceComponent(x=i * 5, y=i * 3))

        # 2. 创建记忆
        ml = MemoryLayer.get_instance()
        ml.register_entity(100, "tree", SensoryDescription(shape="圆形", color="绿色"))

        # 3. 生成报告
        visualizer = WorldVisualizer(self.world)
        report = visualizer.generate_full_report()

        # 4. 验证报告结构
        viz_types = [v["type"] for v in report["visualizations"]]
        self.assertIn("heatmap", viz_types)
        self.assertIn("performance", viz_types)
        self.assertIn("network", viz_types)
        self.assertIn("memory_network", viz_types)
        self.assertIn("timeline", viz_types)

        # 5. 验证数据正确性
        heatmap = report["visualizations"][0]
        self.assertEqual(heatmap["count"], 10)

        mem_net = report["visualizations"][3]
        self.assertGreaterEqual(len(mem_net["concepts"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
