#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物繁殖状态组件 — 纯数据版

v3.9 迁移：移除所有业务逻辑方法，迁移到 AnimalReproductionSystem。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class AnimalReproductionComponent(Component):
    """
    动物繁殖组件 — 纯数据

    属性:
        last_reproduction_tick: 上次繁殖的时间戳
        reproduction_count: 累计繁殖次数
        cooldown_ticks: 当前冷却期长度
        is_pregnant: 是否怀孕
        pregnancy_tick: 怀孕开始时间
        pregnancy_duration: 怀孕持续时间
        mate_id: 当前配偶 ID
    """
    last_reproduction_tick: int = -9999
    reproduction_count: int = 0
    cooldown_ticks: int = 20
    is_pregnant: bool = False
    pregnancy_tick: int = 0
    pregnancy_duration: int = 50
    mate_id: int = -1
