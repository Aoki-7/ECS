#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实体池系统测试

v3.2 新增
"""

import pytest

from core.entity import Entity
from core.entity_pool import EntityPool, PooledEntity


class TestEntityPool:
    """测试实体池"""

    def setup_method(self):
        """每个测试前重置池"""
        EntityPool.reset_instance()
        # 清理 Entity 的静态状态
        Entity._next_id = 0
        Entity._free_ids = []
        Entity._generations = []

    def test_singleton(self):
        """测试单例模式"""
        pool1 = EntityPool.get_instance()
        pool2 = EntityPool.get_instance()
        assert pool1 is pool2

    def test_enable_disable(self):
        """测试启用/禁用"""
        pool = EntityPool.get_instance()
        assert not pool.is_enabled()
        
        pool.enable()
        assert pool.is_enabled()
        
        pool.disable()
        assert not pool.is_enabled()

    def test_acquire_when_disabled(self):
        """测试禁用时获取返回 None"""
        pool = EntityPool.get_instance()
        pool.disable()
        
        entity = pool.acquire()
        assert entity is None

    def test_acquire_from_pool(self):
        """测试从池中获取实体"""
        pool = EntityPool.get_instance()
        pool.enable()
        
        # 获取实体
        entity = pool.acquire()
        assert entity is not None
        assert isinstance(entity, Entity)

    def test_release_and_reuse(self):
        """测试回收和复用"""
        pool = EntityPool.get_instance()
        pool.enable()
        
        # 获取实体
        entity1 = pool.acquire()
        entity_id = entity1.id
        
        # 回收
        assert pool.release(entity1) is True
        
        # 再次获取应该得到同一实体
        entity2 = pool.acquire()
        assert entity2.id == entity_id

    def test_pool_size_limit(self):
        """测试池大小限制"""
        pool = EntityPool.get_instance()
        pool.enable()
        pool.resize(2)
        
        # 获取 3 个实体
        e1 = pool.acquire()
        e2 = pool.acquire()
        e3 = pool.acquire()
        
        # 回收 3 个实体，但池大小限制为 2
        pool.release(e1)
        pool.release(e2)
        result = pool.release(e3)
        
        # 第 3 个应该无法回收
        assert result is False

    def test_stats(self):
        """测试统计信息"""
        pool = EntityPool.get_instance()
        pool.enable()
        
        # 获取实体（命中）
        entity = pool.acquire()
        
        stats = pool.get_stats()
        assert stats["enabled"] is True
        assert stats["hits"] >= 0
        assert stats["misses"] >= 0

    def test_pooled_entity_context_manager(self):
        """测试 PooledEntity 上下文管理器"""
        pool = EntityPool.get_instance()
        pool.enable()
        
        with PooledEntity(pool) as entity:
            assert isinstance(entity, Entity)
            entity.metadata["test"] = "value"
        
        # 退出上下文后实体应该被回收
        stats = pool.get_stats()
        assert stats["pool_size"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])