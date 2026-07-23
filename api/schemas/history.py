#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic 模型 — History 相关

版本: v4.0
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional


class HistoryEntry(BaseModel):
    """历史记录条目"""
    id: int
    tick: int
    entity_id: Optional[int] = None
    event_type: str
    event_data: Dict[str, Any] = {}
    created_at: str


class TimelineEvent(BaseModel):
    """时间轴事件"""
    tick: int
    events: list[HistoryEntry] = []