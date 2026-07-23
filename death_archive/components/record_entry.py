#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
RecordEntry — 死亡档案条目

纯数据记录，描述一个死亡实体的关键信息。
"""

from typing import NamedTuple


class RecordEntry(NamedTuple):
    """
    死亡档案条目

    Fields:
        entity_id: 死亡实体 ID
        entity_name: 实体名称
        entity_type: 实体类型（human / animal / plant / creature）
        death_reason: 死亡原因
        death_time: 死亡时的世界时间（小时）
        death_time_display: 死亡时间的人类可读字符串
        decay_progress: 尸体腐烂进度（0.0 ~ 1.0）
        is_decayed: 尸体是否已完全腐烂
    """
    entity_id: int
    entity_name: str
    entity_type: str
    death_reason: str
    death_time: float
    death_time_display: str
    decay_progress: float
    is_decayed: bool