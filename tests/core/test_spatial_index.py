#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空间索引测试

v3.6 新增
"""

import pytest

from core.spatial_index import SpatialIndex


class TestSpatialIndex:
    """测试空间索引"""

    def test_insert_and_query(self):
        """测试插入和范围查询"""
        index = SpatialIndex(cell_size=10.0)
        
        # 插入实体
        index.insert(1, 5.0, 5.0)
        index.insert(2, 15.0, 15.0)
        index.insert(3, 100.0, 100.0)
        
        # 查询范围
        result = index.query_range(0, 0, 20.0)
        assert 1 in result
        assert 3 not in result

    def test_remove(self):
        """测试移除"""
        index = SpatialIndex(cell_size=10.0)
        index.insert(1, 5.0, 5.0)
        
        index.remove(1)
        result = index.query_range(0, 0, 20.0)
        assert 1 not in result

    def test_update(self):
        """测试更新位置"""
        index = SpatialIndex(cell_size=10.0)
        index.insert(1, 5.0, 5.0)
        
        # 移动实体
        index.update(1, 100.0, 100.0)
        
        # 旧位置不应找到
        result_old = index.query_range(0, 0, 20.0)
        assert 1 not in result_old
        
        # 新位置应找到
        result_new = index.query_range(100, 100, 20.0)
        assert 1 in result_new

    def test_nearest(self):
        """测试最近邻查询"""
        index = SpatialIndex(cell_size=10.0)
        index.insert(1, 0.0, 0.0)
        index.insert(2, 5.0, 0.0)
        index.insert(3, 100.0, 100.0)
        
        nearest = index.query_nearest(0, 0, k=2)
        assert len(nearest) == 2
        # 最近的应该是实体1或2
        assert nearest[0][0] in [1, 2]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])