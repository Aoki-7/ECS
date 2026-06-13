#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖注入层 — WorldManager 单例管理

提供线程安全的 World 实例访问:
    - 单例模式确保全局只有一个 World
    - 使用 asyncio.Lock 保证异步安全
    - 提供序列化/反序列化接口

版本: v4.0
"""

import asyncio
from typing import Optional

from core.world import World


class WorldManager:
    """
    World 管理器 (单例)

    职责:
        1. 维护全局 World 实例
        2. 提供线程安全访问
        3. 序列化/反序列化 World 状态
        4. 快照管理
    """

    _instance: Optional["WorldManager"] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._world = None
            cls._instance._running = False
            cls._instance._paused = False
        return cls._instance

    def get_world(self) -> World:
        """获取 World 实例 (懒加载)"""
        if self._world is None:
            self._world = World()
        return self._world

    def reset_world(self) -> World:
        """重置 World 实例"""
        self._world = World()
        self._running = False
        self._paused = False
        return self._world

    def is_running(self) -> bool:
        """检查模拟是否运行中"""
        return self._running

    def is_paused(self) -> bool:
        """检查模拟是否暂停"""
        return self._paused

    def set_running(self, running: bool) -> None:
        self._running = running

    def set_paused(self, paused: bool) -> None:
        self._paused = paused

    async def run_step(self, dt: float = 1.0) -> None:
        """执行单步模拟"""
        async with self._lock:
            world = self.get_world()
            if not self._paused:
                world.update(dt)

    def get_stats(self) -> dict:
        """获取 World 统计信息"""
        world = self.get_world()
        return world.get_stats()

    def get_cached_stats(self) -> dict:
        """获取缓存的统计信息 (减少计算)"""
        if not hasattr(self, '_stats_cache'):
            self._stats_cache = {}
        
        # 简单缓存策略：每 100 tick 更新一次
        current_tick = getattr(self._world, 'tick', 0)
        last_tick = self._stats_cache.get('_tick', 0)
        
        if current_tick - last_tick >= 100 or not self._stats_cache:
            self._stats_cache = self.get_stats()
            self._stats_cache['_tick'] = current_tick
        
        return self._stats_cache


# 依赖注入函数
def get_world_manager() -> WorldManager:
    return WorldManager()
