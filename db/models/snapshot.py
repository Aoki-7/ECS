#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快照模型

版本: v4.0
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Snapshot:
    """快照数据类"""
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    world_data: bytes = b""
    stats: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Snapshot":
        """从数据库行创建快照"""
        return cls(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            world_data=row["world_data"],
            stats=row["stats"],
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
            "name": self.name,
            "description": self.description,
            "stats": self.stats,
            "created_at": created_at_str,
            "size": len(self.world_data),
        }
