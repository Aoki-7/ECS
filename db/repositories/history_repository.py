#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录仓库 — 数据访问层

提供历史记录的 CRUD 操作:
    - create: 创建历史记录
    - get_by_tick: 根据 tick 获取
    - get_by_entity: 根据实体 ID 获取
    - list_all: 获取所有历史记录

版本: v4.0
"""

import sqlite3
import json
from typing import List, Optional

from db.config import get_db
from db.models.history import HistoryEntry


class HistoryRepository:
    """历史记录仓库"""

    @staticmethod
    def create(entry: HistoryEntry) -> HistoryEntry:
        """创建历史记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            event_data = json.dumps(entry.event_data) if entry.event_data else None
            cursor.execute(
                '''INSERT INTO history (tick, entity_id, event_type, event_data)
                   VALUES (?, ?, ?, ?)''',
                (entry.tick, entry.entity_id, entry.event_type, event_data)
            )
            conn.commit()
            entry.id = cursor.lastrowid
            return entry

    @staticmethod
    def get_by_tick(tick: int, limit: int = 100) -> List[HistoryEntry]:
        """根据 tick 获取历史记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM history WHERE tick = ? ORDER BY created_at LIMIT ?',
                (tick, limit)
            )
            rows = cursor.fetchall()
            return [HistoryEntry.from_row(row) for row in rows]

    @staticmethod
    def get_by_entity(entity_id: int, limit: int = 100) -> List[HistoryEntry]:
        """根据实体 ID 获取历史记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM history WHERE entity_id = ? ORDER BY tick DESC LIMIT ?',
                (entity_id, limit)
            )
            rows = cursor.fetchall()
            return [HistoryEntry.from_row(row) for row in rows]

    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[HistoryEntry]:
        """获取所有历史记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM history ORDER BY tick DESC LIMIT ? OFFSET ?',
                (limit, offset)
            )
            rows = cursor.fetchall()
            return [HistoryEntry.from_row(row) for row in rows]

    @staticmethod
    def get_timeline(start_tick: int = 0, end_tick: Optional[int] = None) -> List[HistoryEntry]:
        """获取时间轴"""
        with get_db() as conn:
            cursor = conn.cursor()
            if end_tick is not None:
                cursor.execute(
                    'SELECT * FROM history WHERE tick >= ? AND tick <= ? ORDER BY tick',
                    (start_tick, end_tick)
                )
            else:
                cursor.execute(
                    'SELECT * FROM history WHERE tick >= ? ORDER BY tick',
                    (start_tick,)
                )
            rows = cursor.fetchall()
            return [HistoryEntry.from_row(row) for row in rows]

    @staticmethod
    def count() -> int:
        """获取历史记录数量"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM history')
            return cursor.fetchone()[0]