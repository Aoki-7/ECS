#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物记忆组件 — 纯数据版

v3.9 迁移：移除所有业务逻辑方法，迁移到 AnimalMemorySystem。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.component import Component


@dataclass
class MemoryEntry:
    """单条记忆条目"""
    x: float
    y: float
    entity_id: int = -1
    memory_type: str = "unknown"  # food, water, threat, mate, shelter
    strength: float = 1.0  # 0.0~1.0，记忆强度
    timestamp: float = 0.0  # 世界时间戳
    value: float = 0.0  # 记忆价值（如食物产量、威胁等级）


@dataclass(slots=True)
class AnimalMemoryComponent(Component):
    """
    动物记忆组件 — 纯数据

    属性:
        memories: 记忆列表（按时间排序）
        max_memories: 最大记忆容量
        decay_rate: 记忆衰减率 (每 tick)
        recall_accuracy: 回忆准确度 (0.0~1.0)
    """
    memories: List[MemoryEntry] = field(default_factory=list)
    max_memories: int = 20
    decay_rate: float = 0.01
    recall_accuracy: float = 0.8