#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
EventLogSystem - 世界事件日志系统

v3.9 迁移：从 core/systems/ 移回 identity/，保持 core 层纯粹性。

职责：
- 管理 EventLogComponent 的生命周期
- 提供 add_event / get_events / prune 等业务逻辑
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass

from core.system import System
from core.world import World
from identity.event_log_component import EventLogComponent

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class EventRecord:
    """事件记录"""
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
        return getattr(self, key, default)


class EventLogSystem(System):
    tick_interval = 1
    priority = 5

    DEFAULT_MAX_EVENTS = 10000
    DEFAULT_KEEP_AFTER_PRUNE = 5000

    def __init__(self):
        super().__init__()
        self._max_events = self.DEFAULT_MAX_EVENTS
        self._keep_after_prune = self.DEFAULT_KEEP_AFTER_PRUNE

    def on_add(self, world: World):
        if world.get_world_component(EventLogComponent) is None:
            world.get_world_entity().add_component(EventLogComponent())

    def on_remove(self, world: World):
        """系统移除时清理 EventLogComponent"""
        we = world.get_world_entity()
        if we:
            comp = world.get_component(we, EventLogComponent)
            if comp:
                we.remove_component(EventLogComponent)

    def update(self, world: World, dt: float = 1.0) -> None:
        super().update(world, dt)
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp and len(log_comp.events) > self._max_events:
            self._prune_old_events(log_comp)

    def add_event(self, world: World, event_type: str, description: str,
                  entity_id: Optional[int] = None,
                  target_id: Optional[int] = None,
                  location: Optional[Tuple[float, float]] = None,
                  data: Optional[Dict[str, Any]] = None,
                  severity: str = "info") -> EventRecord:
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            log_comp = EventLogComponent()
            world.get_world_entity().add_component(log_comp)

        current_time = 0.0
        try:
            time_comp = world.get_time()
            if time_comp:
                current_time = time_comp.total_hours
        except (AttributeError, TypeError):
            pass

        record = EventRecord(
            time=current_time,
            step=getattr(world, 'current_tick', 0),
            type=event_type,
            entity_id=entity_id,
            target_id=target_id,
            location=location,
            description=description,
            data=data or {},
            severity=severity,
        )

        log_comp.events.append(record)
        log_comp._index_by_type[event_type].append(record)
        if entity_id is not None:
            log_comp._index_by_entity[entity_id].append(record)
        log_comp.counters[event_type] += 1

        return record

    def get_events(self, world: World, event_type: Optional[str] = None,
                   entity_id: Optional[int] = None,
                   limit: int = 100) -> List[EventRecord]:
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            return []

        if event_type:
            events = log_comp._index_by_type.get(event_type, [])
        elif entity_id is not None:
            events = log_comp._index_by_entity.get(entity_id, [])
        else:
            events = log_comp.events

        return events[-limit:] if limit else events

    def _prune_old_events(self, log_comp: EventLogComponent) -> None:
        if len(log_comp.events) <= self._keep_after_prune:
            return

        keep_count = self._keep_after_prune
        log_comp.events = log_comp.events[-keep_count:]

        log_comp._index_by_type.clear()
        log_comp._index_by_entity.clear()
        for record in log_comp.events:
            log_comp._index_by_type[record.type].append(record)
            if record.entity_id is not None:
                log_comp._index_by_entity[record.entity_id].append(record)

        logger.info(f"[EventLog] 裁剪旧事件，保留最近 {keep_count} 条")


class EventLog:
    """
    事件日志静态工具类（向后兼容 facade）
    所有调用委托给 EventLogSystem 实例。
    """

    @staticmethod
    def _get_system(world: World) -> "EventLogSystem":
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
        return EventLog._get_system(world).get_events(world, limit=n)

    @staticmethod
    def get_by_type(world: World, event_type: str, limit: int = 100) -> List[EventRecord]:
        """按类型获取事件"""
        return EventLog._get_system(world).get_events(world, event_type=event_type, limit=limit)

    @staticmethod
    def get_summary(world: World) -> Dict[str, int]:
        """获取事件统计摘要"""
        return EventLog._get_system(world).get_event_summary(world)
