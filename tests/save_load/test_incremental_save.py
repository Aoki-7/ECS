#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量存档系统测试

v3.0.1
"""

import os
import tempfile
import unittest

from save_load.incremental_save_system import IncrementalSaveSystem


class TestIncrementalSaveSystem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.system = IncrementalSaveSystem(base_path=self.temp_dir)

    def tearDown(self):
        # 清理临时文件
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def test_flatten_unflatten(self):
        """扁平化/还原"""
        data = {"a": {"b": 1, "c": {"d": 2}}, "e": 3}
        flat = self.system._flatten(data)
        self.assertEqual(flat["a.b"], 1)
        self.assertEqual(flat["a.c.d"], 2)
        self.assertEqual(flat["e"], 3)

        restored = self.system._unflatten(flat)
        self.assertEqual(restored["a"]["b"], 1)
        self.assertEqual(restored["a"]["c"]["d"], 2)

    def test_calculate_diff(self):
        """差异计算"""
        old = {"a": 1, "b": 2, "c": 3}
        new = {"a": 1, "b": 5, "d": 4}

        diff = self.system._calculate_diff(old, new)
        self.assertEqual(diff["b"], 5)  # 修改
        self.assertIsNone(diff["c"])  # 删除
        self.assertEqual(diff["d"], 4)  # 新增

    def test_base_save(self):
        """基础存档"""
        data = {"world": {"tick": 100}, "entities": [1, 2, 3]}
        path = self.system.create_base_save(data, "test_base")

        self.assertTrue(os.path.exists(path + ".gz"))
        self.assertEqual(self.system._incremental_counter, 0)

    def test_incremental_save(self):
        """增量存档"""
        # 创建基础存档
        base_data = {"world": {"tick": 100}, "entities": [1, 2, 3]}
        self.system.create_base_save(base_data, "test")

        # 创建增量存档
        new_data = {"world": {"tick": 101}, "entities": [1, 2, 3, 4]}
        inc_path = self.system.create_incremental_save(new_data)

        self.assertTrue(os.path.exists(inc_path + ".gz"))
        self.assertEqual(self.system._incremental_counter, 1)

    def test_load_full_state(self):
        """加载完整状态"""
        # 基础存档
        base_data = {"world": {"tick": 100}, "entities": [1, 2, 3]}
        base_path = self.system.create_base_save(base_data, "test")

        # 增量存档
        new_data = {"world": {"tick": 101}, "entities": [1, 2, 3, 4]}
        inc_path = self.system.create_incremental_save(new_data)

        # 加载
        full = self.system.load_full_state(base_path, [inc_path])
        self.assertEqual(full["world"]["tick"], 101)

    def test_no_change_skip(self):
        """无变化跳过"""
        base_data = {"world": {"tick": 100}}
        self.system.create_base_save(base_data, "test")

        # 相同数据
        inc_path = self.system.create_incremental_save(base_data)
        self.assertEqual(inc_path, "")  # 跳过

    def test_cleanup(self):
        """清理旧存档"""
        base_data = {"world": {"tick": 100}}
        self.system.create_base_save(base_data, "test")

        # 创建多个增量
        for i in range(15):
            new_data = {"world": {"tick": 100 + i}}
            self.system.create_incremental_save(new_data)

        # 清理，保留10个
        deleted = self.system.cleanup_old_incrementals(keep_count=10)
        self.assertGreaterEqual(deleted, 4)  # 至少删除4个


if __name__ == "__main__":
    unittest.main()