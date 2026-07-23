#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快照仓库 — 数据访问层

提供快照的 CRUD 操作:
    - create: 创建快照
    - get_by_id: 根据 ID 获取
    - list_all: 获取所有快照
    - delete: 删除快照

版本: v4.0
"""

import sqlite3
from typing import List, Optional

from db.config import get_db
from db.models.snapshot import Snapshot


class SnapshotRepository:
    """快照仓库"""

    @staticmethod
    def create(snapshot: Snapshot) -> Snapshot:
        """创建快照"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO snapshots (name, description, world_data, stats)
                   VALUES (?, ?, ?, ?)''',
                (snapshot.name, snapshot.description, snapshot.world_data, snapshot.stats)
            )
            conn.commit()
            snapshot.id = cursor.lastrowid
            return snapshot

    @staticmethod
    def get_by_id(snapshot_id: int) -> Optional[Snapshot]:
        """根据 ID 获取快照"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM snapshots WHERE id = ?',
                (snapshot_id,)
            )
            row = cursor.fetchone()
            if row:
                return Snapshot.from_row(row)
            return None

    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[Snapshot]:
        """获取所有快照"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM snapshots ORDER BY created_at DESC LIMIT ? OFFSET ?',
                (limit, offset)
            )
            rows = cursor.fetchall()
            return [Snapshot.from_row(row) for row in rows]

    @staticmethod
    def delete(snapshot_id: int) -> bool:
        """删除快照"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM snapshots WHERE id = ?', (snapshot_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def count() -> int:
        """获取快照数量"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM snapshots')
            return cursor.fetchone()[0]