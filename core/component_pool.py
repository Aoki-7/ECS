#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComponentPool — 组件对象池

复用组件对象，减少GC压力，提升实体创建/销毁速度。
所有组件继承自Component基类，自动支持对象池复用。
"""

from typing import Dict, Type, List, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ComponentPool:
    """
    组件对象池单例

    每个组件类型对应一个对象池，存储已销毁的组件实例，创建新组件时优先从池里复用。
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._pools: Dict[Type, List[Any]] = defaultdict(list)
            cls._instance._stats = {
                "hit": 0,
                "miss": 0,
                "recycled": 0,
                "total_created": 0,
            }
        return cls._instance

    def get(self, comp_type: Type, *args, **kwargs):
        """
        从池中获取一个组件实例，没有则新建

        Args:
            comp_type: 组件类型
            *args, **kwargs: 组件初始化参数
        Returns:
            组件实例
        """
        pool = self._pools[comp_type]
        if pool:
            comp = pool.pop()
            # 重置组件状态
            if hasattr(comp, 'reset'):
                comp.reset(*args, **kwargs)
            else:
                # 没有reset方法的组件，直接重新初始化
                comp.__init__(*args, **kwargs)
            self._stats["hit"] += 1
            return comp
        # 池空，新建实例（绕过Component.__new__避免递归）
        self._stats["miss"] += 1
        self._stats["total_created"] += 1
        comp = object.__new__(comp_type)
        comp.__init__(*args, **kwargs)
        return comp

    def recycle(self, comp: Any) -> None:
        """
        回收组件实例到池里

        Args:
            comp: 要回收的组件
        """
        comp_type = type(comp)
        self._pools[comp_type].append(comp)
        self._stats["recycled"] += 1

    def get_stats(self) -> dict:
        """获取对象池统计信息"""
        stats = self._stats.copy()
        stats["pool_sizes"] = {t.__name__: len(p) for t, p in self._pools.items()}
        stats["hit_rate"] = stats["hit"] / (stats["hit"] + stats["miss"]) if (stats["hit"] + stats["miss"]) > 0 else 0.0
        return stats

    def clear(self) -> None:
        """清空所有池，释放内存"""
        self._pools.clear()
        self._stats = {
            "hit": 0,
            "miss": 0,
            "recycled": 0,
            "total_created": 0,
        }


# 全局单例
component_pool = ComponentPool()