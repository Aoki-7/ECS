#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
SaveSlotComponent — 存档槽组件

挂载到 world_entity 上，记录存档元数据（非世界状态本身）。
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from core.component import Component


@dataclass(slots=True)
class SaveSlotComponent(Component):
    """
    存档槽元数据

    Fields:
        slot_name: 存档名称
        save_time: 存档时间（ISO 格式字符串）
        tick_count: 存档时的世界 tick 数
        entity_count: 存档时的实体数量
    """
    slot_name: str = "autosave"
    save_time: Optional[str] = None
    tick_count: int = 0
    entity_count: int = 0