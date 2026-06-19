#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间事件调度器

v3.9 迁移：从 core/ 移回 time_module/，保持 core 层纯粹性。

职责：
    - 注册定时/周期事件
    - 在指定 tick 触发回调
    - 支持一次性、周期性、条件性事件
"""

import heapq
from typing import Callable, Dict, List, Optional, Any

import logging

logger = logging.getLogger(__name__)


class ScheduledEvent:
    """调度事件"""

    def __init__(
        self,
        tick: int,
        callback: Callable,
        args: tuple = (),
        kwargs: Optional[Dict] = None,
        interval: int = 0,
        repeat: int = 1,
        event_id: Optional[int] = None,
    ):
        self.tick = tick
        self.callback = callback
        self.args = args
        self.kwargs = kwargs or {}
        self.interval = interval  # 0 = 一次性
        self.repeat = repeat  # -1 = 无限
        self.event_id = event_id
        self.executed_count = 0

    def __lt__(self, other):
        return self.tick < other.tick


class TimeScheduler:
    """
    时间事件调度器

    基于最小堆实现的高效事件调度。
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._events: List[ScheduledEvent] = []
        self._event_counter = 0
        self._cancelled: set = set()

    def schedule(
        self,
        tick: int,
        callback: Callable,
        args: tuple = (),
        kwargs: Optional[Dict] = None,
        interval: int = 0,
        repeat: int = 1,
    ) -> int:
        """注册事件"""
        self._event_counter += 1
        event = ScheduledEvent(
            tick=tick,
            callback=callback,
            args=args,
            kwargs=kwargs,
            interval=interval,
            repeat=repeat,
            event_id=self._event_counter,
        )
        heapq.heappush(self._events, event)
        return self._event_counter

    def cancel(self, event_id: int) -> bool:
        """取消事件"""
        self._cancelled.add(event_id)
        return True

    def update(self, current_tick: int) -> List[Dict]:
        """更新调度器，执行到期的所有事件。"""
        results = []

        while self._events and self._events[0].tick <= current_tick:
            event = heapq.heappop(self._events)

            if event.event_id in self._cancelled:
                self._cancelled.discard(event.event_id)
                continue

            try:
                result = event.callback(*event.args, **event.kwargs)
                results.append({
                    "event_id": event.event_id,
                    "result": result,
                    "tick": current_tick,
                })
                event.executed_count += 1
            except Exception as e:
                logger.error(f"[Scheduler] 事件执行失败: {e}")
                results.append({
                    "event_id": event.event_id,
                    "error": str(e),
                    "tick": current_tick,
                })

            # 重新调度周期性事件
            if event.interval > 0 and (event.repeat == -1 or event.executed_count < event.repeat):
                event.tick = current_tick + event.interval
                heapq.heappush(self._events, event)

        return results

    def get_pending_count(self) -> int:
        """获取待执行事件数量"""
        return len(self._events)

    def clear(self) -> None:
        """清空所有事件"""
        self._events.clear()
        self._cancelled.clear()

    def get_next_tick(self) -> Optional[int]:
        """获取下一个事件触发 tick"""
        while self._events:
            if self._events[0].event_id not in self._cancelled:
                return self._events[0].tick
            heapq.heappop(self._events)
        return None
