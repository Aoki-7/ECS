#!/usr/bin/env python3
"""
大对象清理工具

v3.9 性能优化

为长期驻留的大对象提供定时清理机制。
"""

import time
from typing import Dict, Any, Optional, Callable
from collections import OrderedDict


class LRUCache:
    """
    LRU 缓存

    带容量限制和过期时间的缓存。
    """

    def __init__(self, maxsize: int = 100, ttl: float = None):
        self.maxsize = maxsize
        self.ttl = ttl  # 过期时间（秒）
        self._cache: OrderedDict[Any, Any] = OrderedDict()
        self._timestamps: Dict[Any, float] = {}

    def get(self, key: Any, default: Any = None) -> Any:
        """获取缓存值"""
        if key in self._cache:
            # 检查过期
            if self.ttl is not None:
                if time.time() - self._timestamps[key] > self.ttl:
                    del self._cache[key]
                    del self._timestamps[key]
                    return default
            # 更新访问顺序
            self._cache.move_to_end(key)
            return self._cache[key]
        return default

    def set(self, key: Any, value: Any) -> None:
        """设置缓存值"""
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.maxsize:
                # 淘汰最久未使用的
                oldest = next(iter(self._cache))
                del self._cache[oldest]
                if oldest in self._timestamps:
                    del self._timestamps[oldest]
        self._cache[key] = value
        self._timestamps[key] = time.time()

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._timestamps.clear()

    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            'size': len(self._cache),
            'maxsize': self.maxsize,
            'ttl': self.ttl,
        }


class TimedCleanup:
    """
    定时清理器

    为对象提供定时清理机制。
    """

    def __init__(self, cleanup_interval: float = 60.0):
        self.cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()
        self._objects: Dict[str, Any] = {}
        self._cleanup_handlers: Dict[str, Callable] = {}

    def register(self, name: str, obj: Any, handler: Callable = None) -> None:
        """注册需要清理的对象"""
        self._objects[name] = obj
        if handler:
            self._cleanup_handlers[name] = handler

    def check_cleanup(self) -> None:
        """检查是否需要清理"""
        if time.time() - self._last_cleanup < self.cleanup_interval:
            return

        self._last_cleanup = time.time()
        for name, obj in self._objects.items():
            handler = self._cleanup_handlers.get(name)
            if handler:
                handler(obj)
            elif hasattr(obj, 'clear'):
                obj.clear()

    def force_cleanup(self) -> None:
        """强制清理所有对象"""
        self._last_cleanup = time.time()
        for name, obj in self._objects.items():
            handler = self._cleanup_handlers.get(name)
            if handler:
                handler(obj)
            elif hasattr(obj, 'clear'):
                obj.clear()