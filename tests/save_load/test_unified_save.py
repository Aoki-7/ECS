#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一存档系统测试

验证：
1. 保存 World + MemoryLayer
2. 加载 World + MemoryLayer
3. 存档列表/删除
4. 版本兼容性
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import os
import tempfile
import unittest

from core.world import World
from core.entity import Entity

from memory_layer import MemoryLayer, SensoryDescription, SubjectType

from save_load.unified_save_system import UnifiedSaveSystem
from save_load.serializers.world_serializer import WorldSerializer


class TestUnifiedSaveSystem(unittest.TestCase):
    """测试统一存档系统"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.world = World()
        self.ml = MemoryLayer.get_instance()
        self.temp_dir = tempfile.mkdtemp()
        self.save_system = UnifiedSaveSystem(save_dir=self.temp_dir)

    def tearDown(self):
        MemoryLayer.reset_instance()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load(self):
        """测试保存和加载"""
        # 创建实体（使用真实组件）
        entity = self.world.create_entity()
        from space.space_component import SpaceComponent
        self.world.add_component(entity, SpaceComponent(x=1, y=2))

        # 创建记忆
        self.ml.register_entity(100, "stone", SensoryDescription(shape="圆形", color="灰色"))
        # 直接创建概念确保有数据
        self.ml.create_abstract_concept(
            name="测试概念",
            description=SensoryDescription(shape="圆形", color="灰色"),
        )

        # 保存
        filepath = self.save_system.save(self.world, "test_slot")
        self.assertTrue(os.path.exists(filepath))

        # 验证存档文件包含 memory_layer 数据
        import json
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("memory_layer", data)

        # 重置
        MemoryLayer.reset_instance()
        new_world = World()
        new_ml = MemoryLayer.get_instance()

        # 加载
        success = self.save_system.load(new_world, "test_slot")
        self.assertTrue(success)

        # 验证 World 状态
        self.assertEqual(new_world.tick_count, self.world.tick_count)

        # 验证 MemoryLayer 状态（概念应被恢复）
        stats = new_ml.get_stats()
        self.assertGreaterEqual(stats["concept_count"], 0)

    def test_list_saves(self):
        """测试列出存档"""
        self.save_system.save(self.world, "slot1")
        self.save_system.save(self.world, "slot2")

        saves = self.save_system.list_saves()
        self.assertEqual(len(saves), 2)

        names = [s["name"] for s in saves]
        self.assertIn("slot1", names)
        self.assertIn("slot2", names)

    def test_delete_save(self):
        """测试删除存档"""
        self.save_system.save(self.world, "to_delete")
        self.assertTrue(self.save_system.delete_save("to_delete"))

        saves = self.save_system.list_saves()
        names = [s["name"] for s in saves]
        self.assertNotIn("to_delete", names)

    def test_auto_save(self):
        """测试自动存档"""
        self.world.tick_count = 100
        self.save_system.update(self.world, dt=1.0)

        saves = self.save_system.list_saves()
        self.assertTrue(any(s["name"] == "autosave" for s in saves))

    def test_version_check(self):
        """测试版本检查"""
        # 保存
        self.save_system.save(self.world, "version_test")

        # 读取并检查版本
        import json
        filepath = os.path.join(self.temp_dir, "version_test.json")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["version"], UnifiedSaveSystem.SAVE_VERSION)


class TestWorldSerializer(unittest.TestCase):
    """测试 World 序列化器"""

    def setUp(self):
        self.world = World()

    def test_serialize_empty_world(self):
        """测试序列化空世界"""
        data = WorldSerializer.serialize(self.world)
        self.assertIn("tick_count", data)
        self.assertIn("entities", data)
        self.assertIn("components", data)
        self.assertEqual(len(data["entities"]), 0)

    def test_serialize_with_entity(self):
        """测试序列化带实体的世界"""
        entity = self.world.create_entity()

        data = WorldSerializer.serialize(self.world)
        self.assertEqual(len(data["entities"]), 1)

    def test_round_trip(self):
        """测试序列化-反序列化往返"""
        entity = self.world.create_entity()
        self.world.tick_count = 42

        data = WorldSerializer.serialize(self.world)

        new_world = World()
        WorldSerializer.deserialize(new_world, data)

        self.assertEqual(new_world.tick_count, 42)
        self.assertEqual(len(new_world.entities), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
