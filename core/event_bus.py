#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件总线系统

统一各模块的事件处理，支持订阅/发布模式。

设计原则：
1. 解耦：事件发布者不需要知道谁在监听
2. 异步：事件处理不会阻塞发布者
3. 可追踪：支持事件历史记录和调试
4. 可过滤：支持按优先级、类型过滤

使用示例：
    bus = EventBus()
    
    # 订阅事件
    bus.subscribe("entity_created", on_entity_created)
    
    # 发布事件
    bus.publish("entity_created", {"entity_id": 42, "type": "human"})
"""

import logging
import uuid
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """
    事件对象

    所有通过事件总线传递的消息都包装为 Event。
    """
    event_type: str                    # 事件类型（如 "entity_created"）
    payload: Dict[str, Any]            # 事件载荷数据
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = 0.0             # 事件发生时间
    source: str = "unknown"            # 事件来源（系统/模块名称）
    priority: int = 0                  # 优先级（越高越先处理）

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "source": self.source,
            "priority": self.priority,
        }


@dataclass
class EventSubscription:
    """事件订阅"""
    handler: Callable[[Event], None]   # 处理函数
    priority: int = 0                  # 处理优先级
    once: bool = False                 # 是否只处理一次
    filter_fn: Optional[Callable[[Event], bool]] = None  # 过滤函数


class EventBus:
    """
    事件总线

    全局单例，统一管理所有事件的分发。
    """

    _instance: Optional["EventBus"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # 订阅表: {event_type: [EventSubscription]}
        self._subscriptions: Dict[str, List[EventSubscription]] = {}

        # 事件历史（用于调试和回放）
        self._history: deque = deque(maxlen=1000)

        # 统计
        self._stats = {
            "published": 0,
            "delivered": 0,
            "dropped": 0,
        }

        # 自动清理配置
        self._auto_cleanup_enabled = True
        self._max_subscriptions_per_type = 100  # 每种事件类型最大订阅数
        self._inactive_threshold = 3600  # 订阅者 inactive 阈值（秒）

    @classmethod
    def get_instance(cls) -> "EventBus":
        """获取全局单例"""
        if cls._instance is None:
            cls._instance = EventBus()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（主要用于测试）"""
        cls._instance = None

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[Event], None],
        priority: int = 0,
        once: bool = False,
        filter_fn: Optional[Callable[[Event], bool]] = None,
    ) -> str:
        """
        订阅事件

        Args:
            event_type: 事件类型
            handler: 处理函数 (event) -> None
            priority: 处理优先级（越高越先执行）
            once: 是否只处理一次后自动取消订阅
            filter_fn: 过滤函数，返回 False 则跳过

        Returns:
            订阅ID（用于取消订阅）
        """
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []

        sub = EventSubscription(
            handler=handler,
            priority=priority,
            once=once,
            filter_fn=filter_fn,
        )
        self._subscriptions[event_type].append(sub)
        # 按优先级排序
        self._subscriptions[event_type].sort(key=lambda s: -s.priority)

        sub_id = f"{event_type}_{id(handler)}"
        logger.debug(f"[EventBus] 订阅 {event_type} (priority={priority})")
        return sub_id

    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]) -> bool:
        """取消订阅"""
        if event_type not in self._subscriptions:
            return False

        subs = self._subscriptions[event_type]
        original_len = len(subs)
        self._subscriptions[event_type] = [
            s for s in subs if s.handler != handler
        ]
        return len(self._subscriptions[event_type]) < original_len

    def publish(self, event_type: str, payload: Dict[str, Any],
                source: str = "unknown", priority: int = 0,
                timestamp: float = 0.0) -> Event:
        """
        发布事件

        Args:
            event_type: 事件类型
            payload: 事件数据
            source: 事件来源
            priority: 事件优先级
            timestamp: 时间戳（0 表示使用当前时间）

        Returns:
            创建的事件对象
        """
        import time as time_module
        event = Event(
            event_type=event_type,
            payload=payload,
            timestamp=timestamp or time_module.time(),
            source=source,
            priority=priority,
        )

        # 记录历史
        self._history.append(event)
        self._stats["published"] += 1

        # 分发事件
        self._dispatch(event)

        return event

    def _dispatch(self, event: Event) -> None:
        """分发事件到所有订阅者"""
        subs = self._subscriptions.get(event.event_type, [])
        if not subs:
            self._stats["dropped"] += 1
            return

        to_remove = []
        for sub in list(subs):
            # 过滤检查
            if sub.filter_fn and not sub.filter_fn(event):
                continue

            try:
                sub.handler(event)
                self._stats["delivered"] += 1
            except Exception as e:
                logger.error(f"[EventBus] 事件处理失败 {event.event_type}: {e}")

            # 标记一次性订阅
            if sub.once:
                to_remove.append(sub)

        # 移除一次性订阅
        if to_remove:
            self._subscriptions[event.event_type] = [
                s for s in subs if s not in to_remove
            ]

        # 自动清理：检查订阅数量是否超过阈值
        if self._auto_cleanup_enabled:
            self._auto_cleanup(event.event_type)

    def _auto_cleanup(self, event_type: str) -> None:
        """自动清理过期订阅"""
        subs = self._subscriptions.get(event_type, [])
        if len(subs) > self._max_subscriptions_per_type:
            # 移除低优先级订阅（保留高优先级）
            subs.sort(key=lambda s: -s.priority)
            self._subscriptions[event_type] = subs[:self._max_subscriptions_per_type]
            logger.warning(f"[EventBus] {event_type} 订阅数超过阈值，已清理至 {self._max_subscriptions_per_type}")

    def enable_auto_cleanup(self, max_subscriptions: int = 100) -> None:
        """启用自动清理"""
        self._auto_cleanup_enabled = True
        self._max_subscriptions_per_type = max_subscriptions

    def disable_auto_cleanup(self) -> None:
        """禁用自动清理"""
        self._auto_cleanup_enabled = False

    def get_history(self, event_type: Optional[str] = None,
                    limit: int = 100) -> List[Event]:
        """获取事件历史"""
        events = list(self._history)
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self._stats,
            "subscribed_types": len(self._subscriptions),
            "total_handlers": sum(len(s) for s in self._subscriptions.values()),
            "history_size": len(self._history),
        }

    def clear_history(self) -> None:
        """清空历史"""
        self._history.clear()

    def reset(self) -> None:
        """重置所有状态"""
        self._subscriptions.clear()
        self._history.clear()
        self._stats = {
            "published": 0,
            "delivered": 0,
            "dropped": 0,
        }
