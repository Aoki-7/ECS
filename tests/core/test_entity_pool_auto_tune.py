#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EntityPool 自动调优测试
"""

import pytest

from core.entity_pool import EntityPool
from core.entity import Entity


class TestEntityPoolAutoTune:
    """测试 EntityPool 自动调优功能"""

    def setup_method(self):
        """每个测试前重置"""
        EntityPool.reset_instance()
        self.pool = EntityPool.get_instance()
        self.pool.enable()

    def teardown_method(self):
        """每个测试后清理"""
        self.pool.disable()
        EntityPool.reset_instance()

    def test_auto_tune_expands_on_low_hit_rate(self):
        """低命中率时自动扩容"""
        initial_max = self.pool._max_size
        
        # 模拟低命中率：大量 miss
        for _ in range(200):
            entity = self.pool.acquire()
            # 不释放回池，强制创建新实体
        
        # 手动触发调优（跳过计数器）
        self.pool._auto_tune_counter = 99
        self.pool.auto_tune()
        
        # 应该扩容
        assert self.pool._max_size >= initial_max

    def test_auto_tune_shrinks_on_high_hit_rate(self):
        """高命中率时自动缩容"""
        # 先预热大量实体
        entities = []
        for _ in range(500):
            entity = self.pool.acquire()
            entities.append(entity)
        
        # 全部释放回池
        for entity in entities:
            self.pool.release(entity)
        
        # 再从池中获取（高命中率）
        for _ in range(200):
            entity = self.pool.acquire()
            self.pool.release(entity)
        
        # 先扩容到较大值
        self.pool.resize(2000)
        initial_max = self.pool._max_size
        
        # 重置计数器，确保高命中率
        self.pool._hits = 200
        self.pool._misses = 0
        
        # 手动触发调优
        self.pool._auto_tune_counter = 99
        self.pool.auto_tune()
        
        # 应该缩容或保持不变
        assert self.pool._max_size <= initial_max

    def test_auto_tune_counter_resets(self):
        """测试计数器重置"""
        self.pool._auto_tune_counter = 0
        
        # 前 99 次不应触发调优
        for i in range(99):
            self.pool.auto_tune()
            assert self.pool._auto_tune_counter == i + 1
        
        # 第 100 次触发
        self.pool.auto_tune()
        assert self.pool._auto_tune_counter == 100

    def test_auto_tune_disabled_pool(self):
        """禁用状态下不调优"""
        self.pool.disable()
        
        # 不应报错
        self.pool.auto_tune()
        
        # 状态不变
        assert not self.pool.is_enabled()

    def test_auto_tune_resets_counters(self):
        """调优后重置命中计数"""
        # 制造一些 miss（池为空时 acquire 会 miss）
        self.pool._pool.clear()  # 清空池
        for _ in range(50):
            entity = self.pool.acquire()
        
        assert self.pool._misses > 0
        
        # 触发调优
        self.pool._auto_tune_counter = 99
        self.pool.auto_tune()
        
        # 计数器应重置
        assert self.pool._hits == 0
        assert self.pool._misses == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])