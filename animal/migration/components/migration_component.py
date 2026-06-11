#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁徙组件

v3.6 新增 — P0

职责：
    - 存储动物迁徙状态
    - 记录繁殖地/越冬地、迁徙路线、能量储备

设计原则：
    - 纯物理量驱动：温度、光周期、食物可用性
    - 无硬编码迁徙时间，由环境条件自发决定
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.component import Component


@dataclass
class MigrationComponent(Component):
    """
    迁徙组件

    迁徙驱动因子：
    - 温度变化 → 离开/到达触发
    - 光周期 → 迁徙方向（春季北迁/秋季南迁）
    - 食物可用性 → 停留/离开决策
    - 能量储备 → 迁徙能力

    Attributes:
        is_migratory: 是否迁徙物种
        migration_status: 迁徙状态
            - resident: 定居
            - pre_migratory: 迁徙前准备
            - migrating: 迁徙中
            - arrived: 已到达
        breeding_ground: 繁殖地坐标 (x, y)
        wintering_ground: 越冬地坐标 (x, y)
        current_target: 当前目标坐标
        migration_route: 迁徙路线点列表
        energy_reserve: 能量储备 (0-1)
        migration_speed: 迁徙速度
        temperature_threshold_depart: 离开温度阈值
        temperature_threshold_arrive: 到达温度阈值
        day_length_trigger: 光周期触发点（小时）
    """

    is_migratory: bool = False
    migration_status: str = "resident"
    breeding_ground: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    wintering_ground: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    current_target: Optional[Tuple[float, float]] = None
    migration_route: List[Tuple[float, float]] = field(default_factory=list)
    energy_reserve: float = 1.0
    migration_speed: float = 1.0
    temperature_threshold_depart: float = 10.0
    temperature_threshold_arrive: float = 15.0
    day_length_trigger: float = 12.0

    def to_dict(self) -> dict:
        return {
            "is_migratory": self.is_migratory,
            "migration_status": self.migration_status,
            "breeding_ground": list(self.breeding_ground),
            "wintering_ground": list(self.wintering_ground),
            "current_target": list(self.current_target) if self.current_target else None,
            "migration_route": [list(p) for p in self.migration_route],
            "energy_reserve": self.energy_reserve,
            "migration_speed": self.migration_speed,
            "temperature_threshold_depart": self.temperature_threshold_depart,
            "temperature_threshold_arrive": self.temperature_threshold_arrive,
            "day_length_trigger": self.day_length_trigger,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MigrationComponent":
        target = data.get("current_target")
        return cls(
            is_migratory=data.get("is_migratory", False),
            migration_status=data.get("migration_status", "resident"),
            breeding_ground=tuple(data.get("breeding_ground", [0.0, 0.0])),
            wintering_ground=tuple(data.get("wintering_ground", [0.0, 0.0])),
            current_target=tuple(target) if target else None,
            migration_route=[tuple(p) for p in data.get("migration_route", [])],
            energy_reserve=data.get("energy_reserve", 1.0),
            migration_speed=data.get("migration_speed", 1.0),
            temperature_threshold_depart=data.get("temperature_threshold_depart", 10.0),
            temperature_threshold_arrive=data.get("temperature_threshold_arrive", 15.0),
            day_length_trigger=data.get("day_length_trigger", 12.0),
        )

    def should_depart_spring(self, temperature: float, day_length: float) -> bool:
        """
        春季北迁条件
        温度适宜 + 光周期变长
        """
        temp_ok = temperature >= self.temperature_threshold_depart
        day_ok = day_length > self.day_length_trigger
        energy_ok = self.energy_reserve > 0.3
        return temp_ok and day_ok and energy_ok

    def should_depart_autumn(self, temperature: float, day_length: float) -> bool:
        """
        秋季南迁条件
        温度降低 + 光周期变短
        """
        temp_ok = temperature < self.temperature_threshold_depart
        day_ok = day_length < self.day_length_trigger
        energy_ok = self.energy_reserve > 0.3
        return temp_ok and day_ok and energy_ok

    def can_arrive(self, temperature: float) -> bool:
        """
        到达条件
        温度适宜
        """
        return temperature >= self.temperature_threshold_arrive
