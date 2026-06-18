#!/usr/bin/env python3
"""
SqrtCache - 平方根缓存工具

v3.9 性能优化

为频繁计算的 sqrt 提供缓存，减少重复计算。
"""

import math
from functools import lru_cache
from typing import Tuple


class SqrtCache:
    """
    平方根缓存

    使用 LRU 缓存存储常用距离的平方根。
    适用于空间查询中大量重复的距离计算。
    """

    def __init__(self, maxsize: int = 1024):
        self._cache = {}
        self._maxsize = maxsize
        self._access_order = []

    def get(self, x: float) -> float:
        """获取平方根（带缓存）"""
        key = round(x, 6)  # 精度到 6 位小数
        if key in self._cache:
            # 更新访问顺序
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        
        result = math.sqrt(x)
        
        # 缓存管理
        if len(self._cache) >= self._maxsize:
            # 淘汰最久未使用的
            oldest = self._access_order.pop(0)
            del self._cache[oldest]
        
        self._cache[key] = result
        self._access_order.append(key)
        return result

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._access_order.clear()

    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            'size': len(self._cache),
            'maxsize': self._maxsize,
        }


# 全局单例缓存
_global_sqrt_cache = SqrtCache(maxsize=2048)


def cached_sqrt(x: float) -> float:
    """使用全局缓存的平方根"""
    return _global_sqrt_cache.get(x)


def clear_sqrt_cache() -> None:
    """清空全局平方根缓存"""
    _global_sqrt_cache.clear()


# 距离缓存：缓存 (dx, dy) -> distance
_distance_cache = {}


def cached_distance(dx: float, dy: float) -> float:
    """缓存距离计算"""
    key = (round(dx, 3), round(dy, 3))
    if key not in _distance_cache:
        _distance_cache[key] = math.sqrt(dx*dx + dy*dy)
    return _distance_cache[key]


def clear_distance_cache() -> None:
    """清空距离缓存"""
    _distance_cache.clear()
