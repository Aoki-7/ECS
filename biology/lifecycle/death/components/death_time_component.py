#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
DeathTimeComponent — 死亡时间记录组件

DeathSystem 执行死亡时记录死亡发生的精确世界时间，
供 CorpseSystem（尸体腐败）、人口统计、社会记忆等系统使用。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass
class DeathTimeComponent(Component):
    """
    死亡时间戳。

    Fields:
        world_time_hours: 死亡时的世界累计时间（小时）
        world_time_display: 人类可读的时间字符串，如 "Year 1, Day 45, 14:00"
    """
    world_time_hours: float = 0.0
    world_time_display: str = ""