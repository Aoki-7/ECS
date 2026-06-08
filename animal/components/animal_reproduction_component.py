#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物繁殖状态组件

存储动物的繁殖相关状态，替代 System 级的 dict 状态。
ECS 原则：实体状态应存储在 Component 中。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class AnimalReproductionComponent(Component):
    """
    动物繁殖组件

    属性:
        last_reproduction_tick: 上次繁殖的时间戳 (tick 计数)
        reproduction_count: 累计繁殖次数
        cooldown_ticks: 当前冷却期长度
        is_pregnant: 是否怀孕（仅雌性）
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

    def is_ready(self, current_tick: int) -> bool:
        """检查是否已过冷却期"""
        return (current_tick - self.last_reproduction_tick) >= self.cooldown_ticks

    def record_reproduction(self, current_tick: int) -> None:
        """记录一次繁殖"""
        self.last_reproduction_tick = current_tick
        self.reproduction_count += 1

    def start_pregnancy(self, current_tick: int, mate_id: int) -> None:
        """开始怀孕"""
        self.is_pregnant = True
        self.pregnancy_tick = current_tick
        self.mate_id = mate_id

    def check_birth_ready(self, current_tick: int) -> bool:
        """检查是否到分娩时间"""
        if not self.is_pregnant:
            return False
        return (current_tick - self.pregnancy_tick) >= self.pregnancy_duration

    def give_birth(self) -> None:
        """分娩后重置状态"""
        self.is_pregnant = False
        self.pregnancy_tick = 0
        self.mate_id = -1
