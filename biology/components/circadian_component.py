#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
昼夜节律组件

v3.0.3 新增 — P0

职责：
    - 存储生物的昼夜节律状态
    - 记录睡眠/觉醒周期
    - 影响行为和生理

设计原则：
    - 纯数据组件，无业务逻辑
    - 节律参数因物种而异
"""

from dataclasses import dataclass, field
from typing import Optional

from core.component import Component


@dataclass
class CircadianComponent(Component):
    """
    昼夜节律组件

    Attributes:
        phase: 当前节律相位（0.0-1.0，0=午夜，0.5=正午）
        period: 节律周期（tick数，默认24*60=1440，即24小时）
        activity_peak: 活动高峰相位（0.0-1.0）
        sleep_peak: 睡眠高峰相位（0.0-1.0）
        is_diurnal: 是否昼行性（True=白天活动，False=夜行性）
        sleep_debt: 睡眠债务（0.0-1.0，越高越困）
        last_sleep_tick: 上次睡眠tick
        awake_duration: 连续清醒时长（tick）
        sleep_quality: 睡眠质量（0.0-1.0）
    """

    phase: float = 0.0  # 0.0=午夜, 0.5=正午
    period: float = 1440.0  # 24小时 * 60分钟
    activity_peak: float = 0.5  # 正午活动高峰
    sleep_peak: float = 0.0  # 午夜睡眠高峰
    is_diurnal: bool = True  # 昼行性
    sleep_debt: float = 0.0  # 睡眠债务
    last_sleep_tick: int = 0  # 上次睡眠tick
    awake_duration: int = 0  # 连续清醒时长
    sleep_quality: float = 1.0  # 睡眠质量

    # 节律强度（影响行为程度，0.0=无节律，1.0=严格节律）
    rhythm_strength: float = 0.8

    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "period": self.period,
            "activity_peak": self.activity_peak,
            "sleep_peak": self.sleep_peak,
            "is_diurnal": self.is_diurnal,
            "sleep_debt": self.sleep_debt,
            "last_sleep_tick": self.last_sleep_tick,
            "awake_duration": self.awake_duration,
            "sleep_quality": self.sleep_quality,
            "rhythm_strength": self.rhythm_strength,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CircadianComponent":
        return cls(
            phase=data.get("phase", 0.0),
            period=data.get("period", 1440.0),
            activity_peak=data.get("activity_peak", 0.5),
            sleep_peak=data.get("sleep_peak", 0.0),
            is_diurnal=data.get("is_diurnal", True),
            sleep_debt=data.get("sleep_debt", 0.0),
            last_sleep_tick=data.get("last_sleep_tick", 0),
            awake_duration=data.get("awake_duration", 0),
            sleep_quality=data.get("sleep_quality", 1.0),
            rhythm_strength=data.get("rhythm_strength", 0.8),
        )