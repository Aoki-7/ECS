#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorldEventBus — v4.0 新增

职责：
    - 每 World 独立的事件总线
    - 支持订阅/发布/历史记录
    - 与全局 EventBus 解耦

设计原则：
    - 非单例：每个 World 有自己的事件总线
    - 向后兼容：保持与 EventBus 相同的 API
    - 支持事件历史、优先级、过滤
"""

import logging
import uuid
import bisect
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class WorldEvent:
    """世界事件对象"""
    event_type: str
    payload: Dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = 0.0
    source: str = "unknown"
    priority: int = 0

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "source": self.source,
            "priority": self.priority,
        }


@dataclass
class WorldEventSubscription:
    """世界事件订阅"""
    handler: Callable[[WorldEvent], None]
    priority: int = 0
    once: bool = False
    filter_fn: Optional[Callable[[WorldEvent], bool]] = None


class WorldEventBus:
    """
    世界事件总线

    每 World 独立的事件总线，支持：
    - 订阅/取消订阅
    - 优先级排序
    - 一次性订阅
    - 过滤函数
    - 事件历史
    """

    def __init__(self, world_id: str = "default"):
        self.world_id = world_id

        # 订阅表: {event_type: [WorldEventSubscription]}
        self._subscriptions: Dict[str, List[WorldEventSubscription]] = {}

        # 事件历史
        self._history: deque = deque(maxlen=1000)

        # 异步低优先级事件队列
        self._async_queue: deque = deque()

        # 统计
        self._stats = {
            "published": 0,
            "delivered": 0,
            "async_delivered": 0,
            "filtered": 0,
            "dropped": 0,
        }

    # === 订阅 ===

    def subscribe(self, event_type: str, handler: Callable,
                  priority: int = 0, once: bool = False,
                  filter_fn: Optional[Callable] = None):
        """订阅事件"""
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []

        sub = WorldEventSubscription(handler, priority, once, filter_fn)
        # 按优先级降序插入，避免每次订阅都全量排序
        bisect.insort_left(
            self._subscriptions[event_type], sub,
            key=lambda s: -s.priority
        )

    def unsubscribe(self, event_type: str, handler: Callable):
        """取消订阅"""
        if event_type not in self._subscriptions:
            return

        self._subscriptions[event_type] = [
            s for s in self._subscriptions[event_type]
            if s.handler != handler
        ]

        if not self._subscriptions[event_type]:
            del self._subscriptions[event_type]

    # === 发布 ===

    def publish(self, event_type: str, payload: dict,
                source: str = "unknown", timestamp: float = 0, priority: int = 0) -> None:
        """发布事件
        Args:
            priority: 事件优先级，>=0 同步执行，<0 异步队列执行（每帧末尾批量处理）
        """
        event = WorldEvent(
            event_type=event_type,
            payload=payload,
            timestamp=timestamp,
            source=source,
            priority=priority
        )

        self._history.append(event)
        self._stats["published"] += 1

        if event.priority >= 0:
            # 高优先级：同步分发
            self._dispatch_event(event)
        else:
            # 低优先级：放入异步队列，帧末尾批量处理
            self._async_queue.append(event)

    def _dispatch_event(self, event: WorldEvent) -> None:
        """分发单个事件"""
        subscriptions = self._subscriptions.get(event.event_type, [])
        for sub in list(subscriptions):
            try:
                # 过滤
                if sub.filter_fn and not sub.filter_fn(event):
                    self._stats["filtered"] = self._stats.get("filtered", 0) + 1
                    continue

                sub.handler(event)
                if event.priority >=0:
                    self._stats["delivered"] += 1
                else:
                    self._stats["async_delivered"] += 1

                # 一次性订阅
                if sub.once:
                    self.unsubscribe(event.event_type, sub.handler)

            except Exception as e:
                logger.error(f"[WorldEventBus] 处理事件 {event.event_type} 失败: {e}")
                self._stats["dropped"] += 1

    def process_async_queue(self) -> None:
        """处理所有异步队列中的低优先级事件"""
        while self._async_queue:
            event = self._async_queue.popleft()
            self._dispatch_event(event)

    # === 查询 ===

    def get_history(self, event_type: str = None) -> List[WorldEvent]:
        """获取事件历史"""
        if event_type is None:
            return list(self._history)
        return [e for e in self._history if e.event_type == event_type]

    def get_stats(self) -> dict:
        """获取统计信息"""
        return self._stats.copy()

    def clear_history(self):
        """清空历史"""
        self._history.clear()

    def reset(self):
        """重置总线"""
        self._subscriptions.clear()
        self._history.clear()
        self._stats = {
            "published": 0,
            "delivered": 0,
            "filtered": 0,
            "dropped": 0,
        }
