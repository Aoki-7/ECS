#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录模型

版本: v4.0
"""

import sqlite3
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class HistoryEntry:
    """历史记录数据类"""
    id: Optional[int] = None
    tick: int = 0
    entity_id: Optional[int] = None
    event_type: str = ""
    event_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "HistoryEntry":
        """从数据库行创建历史记录"""
        event_data = None
        if row["event_data"]:
            try:
                event_data = json.loads(row["event_data"])
            except json.JSONDecodeError:
                pass
        
        return cls(
            id=row["id"],
            tick=row["tick"],
            entity_id=row["entity_id"],
            event_type=row["event_type"],
            event_data=event_data,
            created_at=row["created_at"],
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        created_at = self.created_at
        if isinstance(created_at, str):
            created_at_str = created_at
        elif created_at:
            created_at_str = created_at.isoformat()
        else:
            created_at_str = None
        
        return {
            "id": self.id,
            "tick": self.tick,
            "entity_id": self.entity_id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "created_at": created_at_str,
        }