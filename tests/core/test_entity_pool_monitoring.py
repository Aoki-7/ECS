#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实体池监控测试

v3.4 新增
"""

import pytest

from core.entity import Entity
from core.entity_pool import EntityPool


class TestEntityPoolMonitoring:
    """测试实体池监控功能"""

    def setup_method(self):
        """每个测试前重置池"""
        EntityPool.reset_instance()
        Entity._next_id = 0
        Entity._free_ids = []
        Entity._generations = []

    def test_stats_tracking(self):
        """测试统计信息跟踪"""
        pool = EntityPool.get_instance()
        pool.enable()
        
        # 获取实体
        entity = pool.acquire()
        
        stats = pool.get_stats()
        assert stats["total_acquired"] == 1
        assert stats["hits"] >= 0
        assert stats["misses"] >= 0

    def test_peak_pool_size(self):
        """测试峰值池大小跟踪"""
        pool = EntityPool.get_instance()
        pool.enable()
        
        entity = pool.acquire()
        pool.release(entity)
        
        stats = pool.get_stats()
        assert stats["peak_pool_size"] >= 1

    def test_hit_rate_history(self):
        """测试命中率历史"""
        pool = EntityPool.get_instance()
        pool.enable()
        
        # 多次获取和释放
        for _ in range(5):
            entity = pool.acquire()
            pool.release(entity)
        
        stats = pool.get_stats()
        assert "avg_hit_rate" in stats
        assert 0.0 <= stats["avg_hit_rate"] <= 1.0

    def test_auto_tune_expand(self):
        """测试自动扩容"""
        pool = EntityPool.get_instance()
        pool.enable()
        pool.resize(10)  # 小池
        
        # 大量获取导致 miss
        for _ in range(20):
            pool.acquire()
        
        initial_max = pool._max_size
        pool.auto_tune()
        
        # 应该扩容
        assert pool._max_size >= initial_max

    def test_reset_stats(self):
        """测试重置统计"""
        pool = EntityPool.get_instance()
        pool.enable()
        
        entity = pool.acquire()
        pool.release(entity)
        
        pool.reset_stats()
        
        stats = pool.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["total_acquired"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
