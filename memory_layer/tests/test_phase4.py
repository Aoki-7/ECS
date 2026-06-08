#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4 测试

覆盖：
- 记忆持久化（存档/读档）
- 性能基准测试
- 大规模数据压力测试
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import os
import tempfile
import time
import unittest

from memory_layer import (
    MemoryLayer,
    SensoryDescription,
    EmotionalTag,
    SubjectType,
)
from memory_layer.memory_persistence import MemoryPersistence


class TestMemoryPersistence(unittest.TestCase):
    """测试记忆持久化"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.ml = MemoryLayer.get_instance()
        self.temp_dir = tempfile.mkdtemp()
        self.persistence = MemoryPersistence(save_dir=self.temp_dir)

    def tearDown(self):
        MemoryLayer.reset_instance()
        # 清理临时文件
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load(self):
        """测试保存和加载"""
        # 创建一些记忆
        desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
        self.ml.register_entity(1, "stone", desc)
        self.ml.record_contact(
            subject_id=100,
            subject_type=SubjectType.ANIMAL,
            entity_id=1,
            contact_type="visual",
            intensity=0.8,
        )

        # 保存
        filepath = self.persistence.save(self.ml, "test.json")
        self.assertTrue(os.path.exists(filepath))

        # 重置并加载
        MemoryLayer.reset_instance()
        loaded_ml = self.persistence.load("test.json")

        # 验证
        self.assertEqual(loaded_ml.get_stats()["concept_count"], 1)
        self.assertEqual(loaded_ml.get_stats()["memory_count"], 1)

    def test_auto_save(self):
        """测试自动保存"""
        # tick 100 应触发保存
        result = self.persistence.auto_save(self.ml, tick=100, interval=100)
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))

        # tick 101 不应触发
        result = self.persistence.auto_save(self.ml, tick=101, interval=100)
        self.assertIsNone(result)

    def test_list_saves(self):
        """测试列出存档"""
        self.persistence.save(self.ml, "save1.json")
        self.persistence.save(self.ml, "save2.json")

        saves = self.persistence.list_saves()
        self.assertEqual(len(saves), 2)
        self.assertIn("save1.json", saves)
        self.assertIn("save2.json", saves)

    def test_delete_save(self):
        """测试删除存档"""
        self.persistence.save(self.ml, "to_delete.json")
        self.assertTrue(self.persistence.delete_save("to_delete.json"))
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir, "to_delete.json")))


class TestPerformance(unittest.TestCase):
    """性能基准测试"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_bulk_registration_performance(self):
        """测试批量注册性能"""
        count = 1000
        start = time.time()

        for i in range(count):
            desc = SensoryDescription(
                shape="圆形",
                color="灰色",
                texture="光滑",
            )
            self.ml.register_entity(i, "stone", desc)

        elapsed = time.time() - start
        print(f"\n  注册 {count} 个实体: {elapsed:.3f}s ({count/elapsed:.0f}/s)")

        # 应能在 2 秒内完成
        self.assertLess(elapsed, 2.0)

    def test_bulk_contact_performance(self):
        """测试批量记录接触性能"""
        # 先注册实体
        for i in range(100):
            self.ml.register_entity(i, "stone", SensoryDescription(shape="圆形"))

        count = 1000
        start = time.time()

        for i in range(count):
            self.ml.record_contact(
                subject_id=1000 + (i % 10),  # 10 个不同主体
                subject_type=SubjectType.ANIMAL,
                entity_id=i % 100,
                contact_type="visual",
                intensity=0.5,
            )

        elapsed = time.time() - start
        print(f"\n  记录 {count} 次接触: {elapsed:.3f}s ({count/elapsed:.0f}/s)")

        self.assertLess(elapsed, 2.0)

    def test_recall_performance(self):
        """测试回忆性能"""
        # 创建 100 个记忆
        self.ml.register_entity(1, "stone", SensoryDescription(shape="圆形"))
        for i in range(100):
            self.ml.record_contact(
                subject_id=100,
                subject_type=SubjectType.ANIMAL,
                entity_id=1,
                contact_type="visual",
                intensity=0.5,
            )

        # 回忆 1000 次
        count = 1000
        start = time.time()

        for _ in range(count):
            self.ml.recall_memory(100, "entity_1_stone")

        elapsed = time.time() - start
        rate = count / elapsed if elapsed > 0 else float('inf')
        print(f"\n  回忆 {count} 次: {elapsed:.3f}s ({rate:.0f}/s)")

        self.assertLess(elapsed, 1.0)

    def test_memory_capacity(self):
        """测试记忆容量上限"""
        # 设置容量限制
        self.ml._capacity_limit = 500

        # 注册实体
        for i in range(100):
            self.ml.register_entity(i, "stone", SensoryDescription(shape="圆形"))

        # 创建大量记忆
        for i in range(1000):
            self.ml.record_contact(
                subject_id=100,
                subject_type=SubjectType.ANIMAL,
                entity_id=i % 100,
                contact_type="visual",
                intensity=0.5,
            )

        stats = self.ml.get_stats()
        # 记忆数量不应超过容量限制
        self.assertLessEqual(stats["memory_count"], self.ml._capacity_limit)

    def test_serialization_performance(self):
        """测试序列化性能"""
        # 创建大量数据
        for i in range(500):
            self.ml.register_entity(i, "stone", SensoryDescription(shape="圆形"))
            self.ml.record_contact(
                subject_id=100,
                subject_type=SubjectType.ANIMAL,
                entity_id=i,
                contact_type="visual",
                intensity=0.5,
            )

        start = time.time()
        data = self.ml.to_dict()
        elapsed = time.time() - start
        print(f"\n  序列化 {len(data['concepts'])} 概念: {elapsed:.3f}s")

        self.assertLess(elapsed, 1.0)

        # 反序列化
        start = time.time()
        loaded = MemoryLayer.from_dict(data)
        elapsed = time.time() - start
        print(f"  反序列化: {elapsed:.3f}s")

        self.assertLess(elapsed, 1.0)


class TestStress(unittest.TestCase):
    """压力测试"""

    def setUp(self):
        MemoryLayer.reset_instance()
        self.ml = MemoryLayer.get_instance()

    def tearDown(self):
        MemoryLayer.reset_instance()

    def test_large_scale_entities(self):
        """大规模实体测试"""
        entity_count = 5000

        start = time.time()
        for i in range(entity_count):
            self.ml.register_entity(
                i,
                f"type_{i % 10}",
                SensoryDescription(shape="圆形", color="灰色"),
            )
        elapsed = time.time() - start

        print(f"\n  注册 {entity_count} 实体: {elapsed:.3f}s")
        stats = self.ml.get_stats()
        self.assertEqual(stats["concept_count"], entity_count)

    def test_massive_contacts(self):
        """大规模接触测试"""
        # 先注册少量实体
        for i in range(50):
            self.ml.register_entity(i, "stone", SensoryDescription(shape="圆形"))

        contact_count = 10000
        start = time.time()

        for i in range(contact_count):
            self.ml.record_contact(
                subject_id=1000 + (i % 20),
                subject_type=SubjectType.ANIMAL,
                entity_id=i % 50,
                contact_type="visual",
                intensity=0.5,
            )

        elapsed = time.time() - start
        print(f"\n  记录 {contact_count} 次接触: {elapsed:.3f}s ({contact_count/elapsed:.0f}/s)")

        stats = self.ml.get_stats()
        self.assertGreater(stats["memory_count"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
