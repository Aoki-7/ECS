#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控系统

v3.9 新增 — P1

职责：
    - 自动记录所有 System.update() 的执行耗时
    - 统计每帧各 System 的耗时分布
    - 识别性能瓶颈
    - 支持动态启用/禁用

设计原则：
    - 装饰器模式：自动包装 System.update
    - 低开销：仅在启用时记录
    - 数据保留：最近 N 次记录
"""

import time
import logging
from typing import Dict, List, Optional
from collections import deque

from core.system import System
from core.world import World

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    性能监控器

    单例模式，全局监控所有 System 性能。
    """

    _instance: Optional["PerformanceMonitor"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_history: int = 100):
        if getattr(self, '_initialized', False):
            self._max_history = max_history
            return
        self._initialized = True

        self._enabled = False
        self._max_history = max_history
        self._records: Dict[str, deque] = {}  # system_name -> deque of (timestamp, duration_ms)
        self._system_stats: Dict[str, dict] = {}  # system_name -> stats

    @classmethod
    def get_instance(cls) -> "PerformanceMonitor":
        if cls._instance is None:
            cls._instance = PerformanceMonitor()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def enable(self) -> None:
        self._enabled = True
        logger.info("[PerformanceMonitor] 已启用")

    def disable(self) -> None:
        self._enabled = False
        logger.info("[PerformanceMonitor] 已禁用")

    def is_enabled(self) -> bool:
        return self._enabled

    def record(self, system_name: str, duration_ms: float) -> None:
        """记录一次 System 执行耗时"""
        if not self._enabled:
            return

        if system_name not in self._records:
            self._records[system_name] = deque(maxlen=self._max_history)

        self._records[system_name].append((time.time(), duration_ms))

    def get_stats(self, system_name: Optional[str] = None) -> dict:
        """
        获取性能统计

        Args:
            system_name: 指定 System 名称，None 则返回所有

        Returns:
            {
                "system_name": {
                    "count": int,
                    "avg_ms": float,
                    "max_ms": float,
                    "min_ms": float,
                    "total_ms": float,
                }
            }
        """
        if system_name is not None:
            return {system_name: self._calc_stats(system_name)}

        return {name: self._calc_stats(name) for name in self._records.keys()}

    def _calc_stats(self, system_name: str) -> dict:
        """计算单个 System 的统计信息"""
        records = self._records.get(system_name, deque())
        if not records:
            return {"count": 0, "avg_ms": 0.0, "max_ms": 0.0, "min_ms": 0.0, "total_ms": 0.0}

        durations = [r[1] for r in records]
        return {
            "count": len(durations),
            "avg_ms": sum(durations) / len(durations),
            "max_ms": max(durations),
            "min_ms": min(durations),
            "total_ms": sum(durations),
        }

    def get_slow_systems(self, threshold_ms: float = 1.0) -> List[tuple]:
        """
        获取耗时超过阈值的 System

        Returns:
            [(system_name, avg_ms), ...] 按 avg_ms 降序
        """
        slow = []
        for name, stats in self.get_stats().items():
            if stats["avg_ms"] > threshold_ms:
                slow.append((name, stats["avg_ms"]))
        return sorted(slow, key=lambda x: x[1], reverse=True)

    def get_frame_summary(self) -> str:
        """获取帧耗时摘要"""
        stats = self.get_stats()
        if not stats:
            return "暂无性能数据"

        lines = ["=== 性能监控摘要 ==="]
        total_ms = sum(s["total_ms"] for s in stats.values())
        lines.append(f"总监控次数: {sum(s['count'] for s in stats.values())}")
        lines.append(f"总耗时: {total_ms:.2f}ms")
        lines.append("")

        # 按平均耗时排序
        sorted_stats = sorted(stats.items(), key=lambda x: x[1]["avg_ms"], reverse=True)
        for name, s in sorted_stats[:10]:  # 只显示前10
            lines.append(
                f"{name:30s} | 平均: {s['avg_ms']:6.2f}ms | "
                f"最大: {s['max_ms']:6.2f}ms | 次数: {s['count']}"
            )

        return "\n".join(lines)

    def clear(self) -> None:
        """清空所有记录"""
        self._records.clear()
        self._system_stats.clear()


def monitored_update(original_update):
    """
    装饰器：包装 System.update 方法，自动记录性能

    用法：
        class MySystem(System):
            @monitored_update
            def update(self, world, dt):
                ...
    """
    def wrapper(self, world: World, dt: float = 1.0) -> None:
        monitor = PerformanceMonitor.get_instance()
        if not monitor.is_enabled():
            return original_update(self, world, dt)

        start = time.perf_counter()
        try:
            return original_update(self, world, dt)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            monitor.record(self.__class__.__name__, duration_ms)

    return wrapper
