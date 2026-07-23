#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
潮汐组件

v3.5 新增 — P1

职责：
    - 存储潮汐数据
    - 记录潮高、潮时、潮汐类型

设计原则：
    - 纯数据组件，无业务逻辑
    - 支持多种潮汐类型
"""

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component


@dataclass
class TideComponent(Component):
    """
    潮汐组件

    Attributes:
        tide_type: 潮汐类型（semidiurnal/diurnal/mixed）
        high_tide_level: 高潮水位
        low_tide_level: 低潮水位
        current_level: 当前水位
        tide_range: 潮差
        next_high_tide: 下次高潮时间
        next_low_tide: 下次低潮时间
    """

    tide_type: str = "semidiurnal"  # semidiurnal/diurnal/mixed
    high_tide_level: float = 2.0
    low_tide_level: float = -2.0
    current_level: float = 0.0
    tide_range: float = 4.0
    next_high_tide: float = 6.0  # 小时后
    next_low_tide: float = 0.0   # 小时后

    def to_dict(self) -> dict:
        return {
            "tide_type": self.tide_type,
            "high_tide_level": self.high_tide_level,
            "low_tide_level": self.low_tide_level,
            "current_level": self.current_level,
            "tide_range": self.tide_range,
            "next_high_tide": self.next_high_tide,
            "next_low_tide": self.next_low_tide,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TideComponent":
        return cls(
            tide_type=data.get("tide_type", "semidiurnal"),
            high_tide_level=data.get("high_tide_level", 2.0),
            low_tide_level=data.get("low_tide_level", -2.0),
            current_level=data.get("current_level", 0.0),
            tide_range=data.get("tide_range", 4.0),
            next_high_tide=data.get("next_high_tide", 6.0),
            next_low_tide=data.get("next_low_tide", 0.0),
        )