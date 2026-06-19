#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
DeathArchiveComponent — 死亡档案组件

纯数据容器，挂载到 world_entity 上。
集中存储所有死亡实体的档案记录和统计索引。
"""

from dataclasses import dataclass, field
from typing import List, Dict

from core.component import Component
from death_archive.components.record_entry import RecordEntry


@dataclass(slots=True)
class DeathArchiveComponent(Component):
    """
    死亡档案组件 — 中央死亡记录簿

    Fields:
        records: 所有死亡档案列表（按死亡时间升序）
        counters: 按 death_reason 的死亡计数
        index_by_entity: entity_id -> records 索引，用于快速查找
        total_deaths: 累计死亡数
        decayed_count: 已完全腐烂的实体数
    """
    records: List[RecordEntry] = field(default_factory=list)
    counters: Dict[str, int] = field(default_factory=dict)
    index_by_entity: Dict[int, int] = field(default_factory=dict)
    total_deaths: int = 0
    decayed_count: int = 0
