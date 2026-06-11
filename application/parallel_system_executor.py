#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多线程 System 执行器

v3.9 迁移：从 core/ 移回 application/，保持 core 层纯粹性。

职责：
    - 并行执行无依赖的 System
    - 线程安全警告：当前实现不保证 World 状态一致性

设计原则：
    - 仅用于无状态读取的 System（如统计、可视化）
    - 不用于写入 Component 的 System
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List

from core.system import System
from core.world import World

logger = logging.getLogger(__name__)


class ParallelSystemExecutor:
    """
    多线程 System 执行器

    ⚠️ 警告：当前实现不保证 World 状态线程安全。
    仅用于读取型 System，写入型 System 必须单线程执行。
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._executor: ThreadPoolExecutor | None = None
        self._enabled = False

    def enable(self) -> None:
        """启用并行执行"""
        self._enabled = True
        self.start()

    def disable(self) -> None:
        """禁用并行执行"""
        self._enabled = False

    def is_enabled(self) -> bool:
        """是否启用并行执行"""
        return self._enabled

    def start(self) -> None:
        """启动线程池"""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
            logger.info(f"[ParallelExecutor] 线程池启动，max_workers={self.max_workers}")

    def stop(self) -> None:
        """停止线程池"""
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None
            logger.info("[ParallelExecutor] 线程池已关闭")

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "enabled": self._enabled,
            "max_workers": self.max_workers,
        }

    def execute_systems(self, world: World, systems: List[System], dt: float = 1.0) -> None:
        """
        并行执行系统列表

        ⚠️ 警告：所有 System 同时读取 World 状态，可能产生竞态条件。
        仅用于纯读取型 System（如统计、可视化）。
        """
        if self._executor is None:
            self.start()

        def run_system(system: System) -> None:
            try:
                system.update(world, dt)
            except Exception as e:
                logger.error(f"[ParallelExecutor] {system.__class__.__name__} 执行失败: {e}")

        # 提交所有任务
        futures = [self._executor.submit(run_system, s) for s in systems]

        # 等待完成
        for future in futures:
            future.result()
