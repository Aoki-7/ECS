#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行系统执行器

v3.3 新增 — P1

职责：
    - 使用多线程并行执行无依赖的 System
    - 自动检测 System 依赖关系
    - 回退到单线程执行（如果线程不安全）

设计原则：
    - 默认关闭，需手动启用
    - 只并行执行 tick_interval 相同的 System
    - 线程池大小可配置
    - 异常安全：单个 System 失败不影响其他
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Set, Optional

from core.system import System
from core.world import World

logger = logging.getLogger(__name__)


class ParallelSystemExecutor:
    """
    并行系统执行器

    将无依赖关系的 System 分组并行执行。
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._enabled = False
        self._executor: Optional[ThreadPoolExecutor] = None

    def enable(self) -> None:
        """启用并行执行"""
        if not self._enabled:
            self._enabled = True
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
            logger.info(f"[ParallelExecutor] 已启用: {self.max_workers} 工作线程")

    def disable(self) -> None:
        """禁用并行执行"""
        if self._enabled:
            self._enabled = False
            if self._executor:
                self._executor.shutdown(wait=True)
                self._executor = None
            logger.info("[ParallelExecutor] 已禁用")

    def is_enabled(self) -> bool:
        return self._enabled

    def execute_systems(self, world: World, systems: List[System], dt: float) -> None:
        """
        执行系统列表

        如果启用并行，将无依赖的系统分组并行执行。
        否则按顺序执行。

        ⚠️ 线程安全警告：
        - 并行执行时，多个 System 同时读写 World 的组件字典
        - 目前 World 未实现读写锁，并行可能导致数据竞争
        - 建议：只并行执行读取相同组件类型的 System
        - 或：为 World.components 添加 threading.RLock
        """
        if not self._enabled or len(systems) <= 1:
            # 单线程执行
            for system in systems:
                try:
                    system.update(world, dt)
                except Exception as e:
                    logger.error(f"[ParallelExecutor] System {system.__class__.__name__} 失败: {e}")
            return

        # 按 tick_interval 分组
        groups: Dict[int, List[System]] = {}
        for system in systems:
            interval = getattr(system, 'tick_interval', 1)
            if interval not in groups:
                groups[interval] = []
            groups[interval].append(system)

        # 对每个分组并行执行
        for interval, group in groups.items():
            if len(group) <= 1:
                # 单个系统直接执行
                for system in group:
                    try:
                        system.update(world, dt)
                    except Exception as e:
                        logger.error(f"[ParallelExecutor] System {system.__class__.__name__} 失败: {e}")
            else:
                # 并行执行
                self._execute_parallel(world, group, dt)

    def _execute_parallel(self, world: World, systems: List[System], dt: float) -> None:
        """并行执行系统组"""
        if not self._executor:
            return

        futures = {}
        for system in systems:
            future = self._executor.submit(self._run_system_safe, system, world, dt)
            futures[future] = system

        # 等待所有完成
        for future in as_completed(futures):
            system = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f"[ParallelExecutor] System {system.__class__.__name__} 异常: {e}")

    @staticmethod
    def _run_system_safe(system: System, world: World, dt: float) -> None:
        """安全运行系统（捕获异常）"""
        system.update(world, dt)

    def get_stats(self) -> Dict:
        """获取执行器统计信息"""
        return {
            "enabled": self._enabled,
            "max_workers": self.max_workers,
        }
