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

        # 统计
        self._stats = {
            "published": 0,
            "delivered": 0,
            "dropped": 0,
        }

    # === 订阅 ===

    def subscribe(self, event_type: str, handler: Callable,
                  priority: int = 0, once: bool = False,
                  filter_fn: Optional[Callable] = None):
        """订阅事件"""
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []

        self._subscriptions[event_type].append(
            WorldEventSubscription(handler, priority, once, filter_fn)
        )
        # 按优先级排序（高优先级在前）
        self._subscriptions[event_type].sort(
            key=lambda s: s.priority, reverse=True
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
                source: str = "unknown", timestamp: float = 0) -> None:
        """发布事件"""
        event = WorldEvent(
            event_type=event_type,
            payload=payload,
            timestamp=timestamp,
            source=source,
        )

        self._history.append(event)
        self._stats["published"] += 1

        # 分发
        subscriptions = self._subscriptions.get(event_type, [])
        for sub in list(subscriptions):
            try:
                # 过滤
                if sub.filter_fn and not sub.filter_fn(event):
                    continue

                sub.handler(event)
                self._stats["delivered"] += 1

                # 一次性订阅
                if sub.once:
                    self.unsubscribe(event_type, sub.handler)

            except Exception as e:
                logger.error(f"[WorldEventBus] 处理事件 {event_type} 失败: {e}")
                self._stats["dropped"] += 1

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
            "dropped": 0,
        }
