#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录服务 — 业务逻辑层

提供历史记录的业务逻辑:
    - record: 记录事件
    - get_by_tick: 根据 tick 获取
    - get_by_entity: 根据实体 ID 获取
    - get_timeline: 获取时间轴

版本: v4.0
"""

from typing import List, Optional, Dict, Any

from db.repositories.history_repository import HistoryRepository
from db.models.history import HistoryEntry


class HistoryService:
    """历史记录服务"""

    @staticmethod
    def record(tick: int, event_type: str, entity_id: Optional[int] = None, event_data: Optional[Dict[str, Any]] = None) -> HistoryEntry:
        """记录事件"""
        entry = HistoryEntry(
            tick=tick,
            entity_id=entity_id,
            event_type=event_type,
            event_data=event_data,
        )
        return HistoryRepository.create(entry)

    @staticmethod
    def get_by_tick(tick: int, limit: int = 100) -> List[dict]:
        """根据 tick 获取历史记录"""
        entries = HistoryRepository.get_by_tick(tick, limit)
        return [e.to_dict() for e in entries]

    @staticmethod
    def get_by_entity(entity_id: int, limit: int = 100) -> List[dict]:
        """根据实体 ID 获取历史记录"""
        entries = HistoryRepository.get_by_entity(entity_id, limit)
        return [e.to_dict() for e in entries]

    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[dict]:
        """获取所有历史记录"""
        entries = HistoryRepository.list_all(limit, offset)
        return [e.to_dict() for e in entries]

    @staticmethod
    def get_timeline(start_tick: int = 0, end_tick: Optional[int] = None) -> List[dict]:
        """获取时间轴"""
        entries = HistoryRepository.get_timeline(start_tick, end_tick)
        return [e.to_dict() for e in entries]

    @staticmethod
    def count() -> int:
        """获取历史记录数量"""
        return HistoryRepository.count()