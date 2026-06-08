#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
EventLogSystem - 世界事件日志系统

职责：
- 管理 EventLogComponent 的生命周期（自动挂载到 world_entity）
- 提供 add_event / get_events / prune 等业务逻辑
- 通过 EventLog facade 提供向后兼容的静态接口
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass

from core.system import System
from core.world import World
from core.event_log_component import EventLogComponent

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class EventRecord:
    """事件记录 - 替代裸dict，减少小对象开销并提供类型安全"""
    time: float
    step: int
    type: str
    entity_id: Optional[int]
    target_id: Optional[int]
    location: Optional[Tuple[float, float]]
    description: str
    data: Dict[str, Any]
    severity: str

    def get(self, key: str, default=None):
        """向后兼容的 dict.get() 行为"""
        return getattr(self, key, default)


class EventLogSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """世界事件日志系统，管理全局事件记录与查询。"""

    priority = 5  # 与时间系统同级，尽早可用

    # 事件日志上限配置（可通过实例属性覆盖）
    DEFAULT_MAX_EVENTS = 10000
    DEFAULT_KEEP_AFTER_PRUNE = 5000

    def __init__(self):
        super().__init__()
        self._max_events = self.DEFAULT_MAX_EVENTS
        self._keep_after_prune = self.DEFAULT_KEEP_AFTER_PRUNE

    def on_add(self, world: World):
        """自动挂载 EventLogComponent 到 world_entity"""
        if world.get_world_component(EventLogComponent) is None:
            world.get_world_entity().add_component(EventLogComponent())

    def update(self, world: World, dt: float = 1.0) -> None:
        """每 tick 检查是否需要裁剪旧事件"""
        super().update(world, dt)
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp and len(log_comp.events) > self._max_events:
            self._prune_old_events(log_comp)

    # ── 业务逻辑 ──

    def add_event(self, world: World, event_type: str, description: str,
                  entity_id: Optional[int] = None,
                  target_id: Optional[int] = None,
                  location: Optional[Tuple[float, float]] = None,
                  data: Optional[Dict[str, Any]] = None,
                  severity: str = "info") -> EventRecord:
        """添加一条事件记录"""
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            log_comp = EventLogComponent()
            world.get_world_entity().add_component(log_comp)

        current_time = 0.0
        try:
            time_comp = world.get_time()
            if time_comp:
                current_time = time_comp.total_hours
        except (AttributeError, TypeError) as e:
            logger.warning(f"[EventLog] 获取时间失败: {e}")

        step = getattr(world, '_step_count', 0)

        event = EventRecord(
            time=current_time,
            step=step,
            type=event_type,
            entity_id=entity_id,
            target_id=target_id,
            location=location,
            description=description,
            data=data or {},
            severity=severity,
        )

        idx = len(log_comp.events)
        log_comp.events.append(event)

        # 更新索引
        log_comp._index_by_type[event_type].append(idx)
        if entity_id is not None:
            log_comp._index_by_entity[entity_id].append(idx)
        if target_id is not None:
            log_comp._index_by_entity[target_id].append(idx)

        # 更新计数器
        log_comp.counters[event_type] = log_comp.counters.get(event_type, 0) + 1
        if severity in ("critical", "milestone"):
            key = f"severity_{severity}"
            log_comp.counters[key] = log_comp.counters.get(key, 0) + 1

        return event

    def get_events(self, world: World,
                   event_type: Optional[str] = None,
                   entity_id: Optional[int] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[EventRecord]:
        """查询事件（按时间倒序）"""
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            return []

        if event_type is not None and entity_id is not None:
            type_indices = set(log_comp._index_by_type.get(event_type, []))
            entity_indices = set(log_comp._index_by_entity.get(entity_id, []))
            indices = sorted(type_indices & entity_indices, reverse=True)
        elif event_type is not None:
            indices = sorted(log_comp._index_by_type.get(event_type, []), reverse=True)
        elif entity_id is not None:
            indices = sorted(log_comp._index_by_entity.get(entity_id, []), reverse=True)
        else:
            indices = list(range(len(log_comp.events) - 1, -1, -1))

        indices = indices[offset:offset + limit]
        return [log_comp.events[i] for i in indices]

    def get_recent_events(self, world: World, n: int = 20) -> List[EventRecord]:
        """获取最近 N 条事件"""
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            return []
        return log_comp.events[-n:] if n < len(log_comp.events) else log_comp.events.copy()

    def get_event_summary(self, world: World) -> Dict[str, int]:
        """获取事件类型统计摘要"""
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            return {}
        return dict(log_comp.counters)

    def get_events_by_time_range(self, world: World,
                                  start_time: float,
                                  end_time: float) -> List[EventRecord]:
        """获取时间范围内的事件"""
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            return []
        return [
            e for e in log_comp.events
            if start_time <= e.time <= end_time
        ]

    def export_to_list(self, world: World) -> List[EventRecord]:
        """导出所有事件为列表"""
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            return []
        return log_comp.events.copy()

    def _prune_old_events(self, log_comp: EventLogComponent):
        """修剪旧事件，保留最近 _keep_after_prune 条，重建索引与计数器"""
        to_remove = len(log_comp.events) - self._keep_after_prune
        if to_remove <= 0:
            return
        del log_comp.events[:to_remove]

        # 重建索引
        log_comp._index_by_type = defaultdict(list)
        log_comp._index_by_entity = defaultdict(list)
        # 重建计数器
        log_comp.counters = defaultdict(int)
        for idx, event in enumerate(log_comp.events):
            event_type = event.type
            log_comp._index_by_type[event_type].append(idx)
            log_comp.counters[event_type] += 1
            if event.entity_id is not None:
                log_comp._index_by_entity[event.entity_id].append(idx)
            if event.target_id is not None:
                log_comp._index_by_entity[event.target_id].append(idx)
            severity = event.severity
            if severity in ("critical", "milestone"):
                log_comp.counters[f"severity_{severity}"] += 1


class EventLog:
    """
    事件日志静态工具类（向后兼容 facade）
    所有调用委托给 EventLogSystem 实例。
    """

    @staticmethod
    def _get_system(world: World) -> EventLogSystem:
        system = world.get_system(EventLogSystem)
        if system is None:
            system = EventLogSystem()
            world.add_system(system)
        return system

    @staticmethod
    def log(world: World, event_type: str, description: str,
            entity_id: Optional[int] = None,
            target_id: Optional[int] = None,
            location: Optional[Tuple[float, float]] = None,
            data: Optional[Dict[str, Any]] = None,
            severity: str = "info"):
        """记录一条世界事件"""
        return EventLog._get_system(world).add_event(
            world, event_type, description,
            entity_id=entity_id, target_id=target_id,
            location=location, data=data, severity=severity
        )

    @staticmethod
    def get_recent(world: World, n: int = 20) -> List[EventRecord]:
        """获取最近事件"""
        return EventLog._get_system(world).get_recent_events(world, n)

    @staticmethod
    def get_by_type(world: World, event_type: str, limit: int = 100) -> List[EventRecord]:
        """按类型获取事件"""
        return EventLog._get_system(world).get_events(world, event_type=event_type, limit=limit)

    @staticmethod
    def get_summary(world: World) -> Dict[str, int]:
        """获取事件统计摘要"""
        return EventLog._get_system(world).get_event_summary(world)
