#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SystemScheduler — v4.0 核心重构

职责：
    - System 依赖图解析
    - 拓扑排序
    - 按 tick_interval 调度执行
    - 性能监控集成

设计原则：
    - 声明式依赖：System 声明 before/after 依赖
    - 自动拓扑排序：Kahn 算法
    - 循环依赖检测：运行时验证
    - 向后兼容：支持旧版 priority 字段
"""

from __future__ import annotations
import logging
from typing import List, Type, Dict, Set, Optional, Tuple, TYPE_CHECKING
from collections import deque

from core.system import System

if TYPE_CHECKING:
    from core.world import World

logger = logging.getLogger(__name__)


class CircularDependencyError(Exception):
    """循环依赖错误"""
    pass


class SystemScheduler:
    """
    系统调度器

    管理所有 System 的注册、排序、执行。
    """

    def __init__(self):
        self._systems: List[System] = []
        self._sorted: List[System] = []
        self._dirty = True  # 是否需要重新排序

        # 统计
        self._stats = {
            "registered": 0,
            "executed": 0,
            "skipped": 0,
        }

    # === 注册 ===

    def add(self, system: System):
        """
        注册系统

        Args:
            system: 要注册的系统实例
        """
        if any(type(s) is type(system) for s in self._systems):
            logger.debug(f"[SystemScheduler] 跳过重复系统 {type(system).__name__}")
            return
        self._systems.append(system)
        self._stats["registered"] += 1
        self._dirty = True

    def remove(self, system_type: Type[System]) -> bool:
        """
        移除指定类型的系统

        Args:
            system_type: 系统类型

        Returns:
            bool: 是否成功移除
        """
        for i, sys in enumerate(self._systems):
            if isinstance(sys, system_type):
                self._systems.pop(i)
                self._dirty = True
                return True
        return False

    def get(self, system_type: Type[System]) -> Optional[System]:
        """
        获取指定类型的系统

        Args:
            system_type: 系统类型

        Returns:
            System 实例，或 None
        """
        for sys in self._systems:
            if isinstance(sys, system_type):
                return sys
        return None

    def get_all(self) -> List[System]:
        """获取所有注册的系统"""
        return self._systems.copy()

    # === 排序 ===

    def _sort(self) -> List[System]:
        """
        拓扑排序 + 优先级排序

        1. 构建依赖图
        2. Kahn 算法拓扑排序
        3. 同层级内按 priority 排序

        Returns:
            排序后的系统列表

        Raises:
            CircularDependencyError: 检测到循环依赖
        """
        if not self._dirty:
            return self._sorted

        if not self._systems:
            self._sorted = []
            self._dirty = False
            return self._sorted

        # 构建依赖图
        graph = {}
        type_to_instance = {}

        for sys in self._systems:
            sys_type = type(sys)
            type_to_instance[sys_type] = sys

            # 收集依赖
            after = set()
            before = set()

            # 从类属性读取依赖声明
            for dep_type in getattr(sys, 'dependencies_after', []):
                after.add(dep_type)
            for dep_type in getattr(sys, 'dependencies_before', []):
                before.add(dep_type)

            graph[sys_type] = {
                'after': after,
                'before': before,
                'priority': getattr(sys, 'priority', 0),
                'instance': sys,
            }

        # 验证依赖是否存在
        all_types = set(graph.keys())
        for sys_type, info in graph.items():
            for dep in info['after']:
                if dep not in all_types:
                    logger.warning(f"{sys_type.__name__} 依赖未注册的 {dep.__name__}")
            for dep in info['before']:
                if dep not in all_types:
                    logger.warning(f"{sys_type.__name__} 依赖未注册的 {dep.__name__}")

        # 构建邻接表和入度表
        # 边: A -> B 表示 A 必须在 B 之前执行
        adjacency: Dict[Type[System], Set[Type[System]]] = {t: set() for t in all_types}
        in_degree: Dict[Type[System], int] = {t: 0 for t in all_types}

        for sys_type, info in graph.items():
            # after: 我必须在哪些系统之后
            for dep in info['after']:
                if dep in all_types:
                    adjacency[dep].add(sys_type)
                    in_degree[sys_type] += 1

            # before: 我必须在哪些系统之前
            for dep in info['before']:
                if dep in all_types:
                    adjacency[sys_type].add(dep)
                    in_degree[dep] += 1

        # Kahn 算法
        queue = deque()
        for sys_type, degree in in_degree.items():
            if degree == 0:
                queue.append(sys_type)

        sorted_types = []
        while queue:
            # 按 priority 排序，priority 小的先执行
            queue = deque(sorted(queue, key=lambda t: graph[t]['priority']))
            sys_type = queue.popleft()
            sorted_types.append(sys_type)

            for neighbor in adjacency[sys_type]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 检查循环依赖
        if len(sorted_types) != len(all_types):
            remaining = [t.__name__ for t in all_types if t not in sorted_types]
            raise CircularDependencyError(
                f"检测到循环依赖，无法排序的系统: {remaining}"
            )

        self._sorted = [graph[t]['instance'] for t in sorted_types]
        self._dirty = False
        return self._sorted

    # === 执行 ===

    def update(self, world, dt: float):
        """
        执行所有系统

        Args:
            world: 世界实例
            dt: 时间增量
        """
        sorted_systems = self._sort()

        for system in sorted_systems:
            # 兼容非 System 子类的对象（如测试中的 SimpleSystem）
            enabled = getattr(system, 'enabled', True)
            if not enabled:
                self._stats["skipped"] += 1
                continue

            tick_interval = getattr(system, 'tick_interval', 1)
            if world.tick_count % tick_interval != 0:
                self._stats["skipped"] += 1
                continue

            try:
                system.update(world, dt)
                self._stats["executed"] += 1
            except Exception as e:
                logger.error(f"系统 {type(system).__name__} 执行失败: {e}")
                # 一个系统失败不影响其他系统
                continue

    # === 验证 ===

    def validate(self) -> List[str]:
        """
        验证依赖图

        Returns:
            错误列表，空列表表示无错误
        """
        errors = []

        try:
            self._sort()
        except CircularDependencyError as e:
            errors.append(str(e))

        return errors

    # === 统计 ===

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "registered": self._stats["registered"],
            "executed": self._stats["executed"],
            "skipped": self._stats["skipped"],
        }

    def __len__(self) -> int:
        """注册的系统数量"""
        return len(self._systems)

    def get_execution_order(self) -> List[str]:
        """获取执行顺序（用于调试）"""
        sorted_systems = self._sort()
        return [type(s).__name__ for s in sorted_systems]

    # === 重置 ===

    def reset(self):
        """重置调度器（主要用于测试）"""
        self._systems.clear()
        self._sorted.clear()
        self._dirty = True
        self._stats = {
            "registered": 0,
            "executed": 0,
            "skipped": 0,
        }
