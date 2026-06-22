#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实体池系统

v3.2 新增 — P0

职责：
    - 预创建实体对象池，减少运行时 GC 压力
    - 实体销毁时回收到池中而非释放
    - 需要时从池中获取已初始化的实体

设计原则：
    - 与现有 Entity.create() / Entity.destroy() 兼容
    - 可选启用（默认关闭，不影响现有行为）
    - 池大小可配置
    - 线程安全（单线程场景下简单实现）
"""

import logging
from typing import Optional, List
from core.entity import Entity

logger = logging.getLogger(__name__)


class EntityPool:
    """
    实体对象池

    减少频繁创建/销毁实体时的内存分配开销。
    """

    _instance: Optional["EntityPool"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, initial_size: int = 100, max_size: int = 1000):
        if self._initialized:
            return
        self._initialized = True

        self._initial_size = initial_size
        self._max_size = max_size
        self._pool: List[Entity] = []
        self._enabled = False
        self._hits = 0
        self._misses = 0
        
        # 监控数据
        self._total_acquired = 0
        self._total_released = 0
        self._peak_pool_size = 0
        self._resize_count = 0
        self._hit_rate_history: List[float] = []
        self._history_max_size = 100

    @classmethod
    def get_instance(cls) -> "EntityPool":
        """获取全局单例"""
        if cls._instance is None:
            cls._instance = EntityPool()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（主要用于测试）"""
        cls._instance = None

    def enable(self) -> None:
        """启用实体池"""
        if not self._enabled:
            self._enabled = True
            self._prewarm()

    def disable(self) -> None:
        """禁用实体池"""
        self._enabled = False
        self._pool.clear()

    def is_enabled(self) -> bool:
        return self._enabled

    def _prewarm(self) -> None:
        """预热池：预创建实体"""
        # 注意：Entity.create() 会分配 ID，预热时直接创建
        for _ in range(self._initial_size):
            entity = Entity.create()
            self._pool.append(entity)

    def acquire(self) -> Optional[Entity]:
        """
        从池中获取实体

        Returns:
            池中的实体，或 None（池为空且未启用时）
        """
        if not self._enabled:
            return None

        if self._pool:
            self._hits += 1
            self._total_acquired += 1
            return self._pool.pop()

        # 池为空，创建新实体
        self._misses += 1
        self._total_acquired += 1
        return Entity.create()

    def release(self, entity: Entity) -> bool:
        """
        将实体回收到池中

        Returns:
            是否成功回收
        """
        if not self._enabled:
            return False

        if len(self._pool) >= self._max_size:
            return False

        # 重置实体状态（只重置 metadata，保留 id 和 generation）
        entity.metadata.clear()
        
        # 使用 metadata 标记失效状态（避免修改 immutable 实体）
        entity.metadata["_is_active"] = False
        
        self._pool.append(entity)
        self._total_released += 1
        self._peak_pool_size = max(self._peak_pool_size, len(self._pool))
        return True

    def cleanup_expired(self, max_age: int = 100) -> int:
        """
        清理失效实体

        移除池中超过 max_age 代的实体，防止内存泄漏。

        Args:
            max_age: 最大允许的代数差

        Returns:
            清理的实体数量
        """
        if not self._enabled or not self._pool:
            return 0

        # 获取当前全局代
        current_gen = Entity._global_generation if hasattr(Entity, '_global_generation') else 0
        
        cleaned = 0
        new_pool = []
        
        for entity in self._pool:
            entity_gen = getattr(entity, '_generation', 0)
            # 如果实体代数差距过大，说明已经过期
            if current_gen - entity_gen > max_age:
                cleaned += 1
                # 不添加到新池，让 GC 回收
            else:
                new_pool.append(entity)
        
        self._pool = new_pool
        
        if cleaned > 0:
            logger.debug(f"[EntityPool] 清理 {cleaned} 个失效实体")
        
        return cleaned

    def get_stats(self) -> dict:
        """获取池统计信息"""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
        
        # 记录命中率历史
        if total_requests > 0:
            self._hit_rate_history.append(hit_rate)
            if len(self._hit_rate_history) > self._history_max_size:
                self._hit_rate_history = self._hit_rate_history[-self._history_max_size:]
        
        return {
            "enabled": self._enabled,
            "pool_size": len(self._pool),
            "initial_size": self._initial_size,
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "total_acquired": self._total_acquired,
            "total_released": self._total_released,
            "peak_pool_size": self._peak_pool_size,
            "resize_count": self._resize_count,
            "avg_hit_rate": sum(self._hit_rate_history) / len(self._hit_rate_history) if self._hit_rate_history else 0.0,
        }

    def resize(self, new_max_size: int) -> None:
        """调整池大小"""
        self._max_size = new_max_size
        self._resize_count += 1
        # 如果当前池超过新大小，截断
        while len(self._pool) > new_max_size:
            # 从池中移除多余实体，让它们被 GC 回收
            # 注意：这里不调用 Entity.destroy()，因为实体还在池中
            self._pool.pop()

    def auto_tune(self) -> None:
        """
        根据命中率自动调整池大小
        
        策略：
        - 命中率 < 50%：增加池大小
        - 命中率 > 90%：减少池大小
        - 池大小在 [initial_size, max_size * 2] 范围内
        - 每调用 N 次才执行一次（避免每帧都调整）
        """
        if not self._enabled:
            return

        # 累计调用计数
        if not hasattr(self, '_auto_tune_counter'):
            self._auto_tune_counter = 0
        self._auto_tune_counter += 1
        
        # 每 100 次调用执行一次调优
        if self._auto_tune_counter % 100 != 0:
            return

        stats = self.get_stats()
        hit_rate = stats["hit_rate"]
        current_max = self._max_size

        if hit_rate < 0.5 and self._misses > 10:
            # 命中率低，增加池大小
            new_max = min(current_max * 2, current_max + 500)
            if new_max > current_max:
                self.resize(new_max)
                logger.info(f"[EntityPool] 自动扩容: {current_max} -> {new_max} (命中率 {hit_rate:.1%})")
        elif hit_rate > 0.9 and len(self._pool) > self._initial_size:
            # 命中率高，减少池大小
            new_max = max(self._initial_size, current_max // 2)
            if new_max < current_max:
                self.resize(new_max)
                logger.info(f"[EntityPool] 自动缩容: {current_max} -> {new_max} (命中率 {hit_rate:.1%})")
        
        # 重置计数器（保留命中率历史）
        self._hits = 0
        self._misses = 0

    def reset_stats(self) -> None:
        """重置统计数据（保留池）"""
        self._hits = 0
        self._misses = 0
        self._total_acquired = 0
        self._total_released = 0
        self._peak_pool_size = len(self._pool)
        self._resize_count = 0
        self._hit_rate_history.clear()


class PooledEntity:
    """
    支持池化的实体包装器

    使用示例：
        with PooledEntity() as entity:
            world.add_component(entity, SomeComponent())
            # 使用 entity
        # 退出上下文时自动回收到池中
    """

    def __init__(self, pool: Optional[EntityPool] = None):
        self.pool = pool or EntityPool.get_instance()
        self.entity: Optional[Entity] = None

    def __enter__(self) -> Entity:
        if self.pool.is_enabled():
            self.entity = self.pool.acquire()
        if self.entity is None:
            self.entity = Entity.create()
        return self.entity

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.entity is not None:
            # 尝试回收到池中
            if not self.pool.release(self.entity):
                # 池已满，正常销毁
                Entity.destroy(self.entity)
            self.entity = None
