#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物候组件

v3.6 新增 — P0

职责：
    - 存储植物物候状态
    - 记录发芽/开花/结果/落叶等物候期

设计原则：
    - 纯物理量驱动：积温、光周期、水分
    - 无硬编码物候期，由环境条件自发决定
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component


@dataclass
class PhenologyComponent(Component):
    """
    物候组件

    物候期由以下物理量驱动：
    - 积温（Growing Degree Days）→ 发芽/开花
    - 光周期 → 落叶/休眠
    - 土壤水分 → 生长/休眠
    - 温度阈值 → 冻害/复苏

    Attributes:
        phenophase: 当前物候期
            - dormant: 休眠
            - budding: 萌芽
            - leafing: 展叶
            - flowering: 开花
            - fruiting: 结果
            - senescence: 衰老
            - leaf_fall: 落叶
        gdd_accumulated: 累积积温（°C·day）
        gdd_base: 积温基准温度（°C）
        gdd_requirements: 各物候期所需积温
        chill_hours: 需冷量（小时，<7.2°C）
        chill_requirement: 需冷量需求
        day_length_sensitivity: 光周期敏感度
        last_transition_tick: 上次物候转换时间
    """

    phenophase: str = "dormant"
    gdd_accumulated: float = 0.0
    gdd_base: float = 5.0
    gdd_requirements: Dict[str, float] = field(default_factory=lambda: {
        "budding": 50.0,
        "leafing": 150.0,
        "flowering": 300.0,
        "fruiting": 500.0,
        "senescence": 800.0,
        "leaf_fall": 1000.0,
    })
    chill_hours: float = 0.0
    chill_requirement: float = 1000.0
    day_length_sensitivity: float = 0.5
    last_transition_tick: int = 0

    def to_dict(self) -> dict:
        return {
            "phenophase": self.phenophase,
            "gdd_accumulated": self.gdd_accumulated,
            "gdd_base": self.gdd_base,
            "gdd_requirements": self.gdd_requirements.copy(),
            "chill_hours": self.chill_hours,
            "chill_requirement": self.chill_requirement,
            "day_length_sensitivity": self.day_length_sensitivity,
            "last_transition_tick": self.last_transition_tick,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PhenologyComponent":
        return cls(
            phenophase=data.get("phenophase", "dormant"),
            gdd_accumulated=data.get("gdd_accumulated", 0.0),
            gdd_base=data.get("gdd_base", 5.0),
            gdd_requirements=data.get("gdd_requirements", {
                "budding": 50.0,
                "leafing": 150.0,
                "flowering": 300.0,
                "fruiting": 500.0,
                "senescence": 800.0,
                "leaf_fall": 1000.0,
            }),
            chill_hours=data.get("chill_hours", 0.0),
            chill_requirement=data.get("chill_requirement", 1000.0),
            day_length_sensitivity=data.get("day_length_sensitivity", 0.5),
            last_transition_tick=data.get("last_transition_tick", 0),
        )

    def calculate_gdd(self, avg_temperature: float) -> float:
        """
        计算当日积温
        GDD = max(0, T_avg - T_base)
        """
        return max(0.0, avg_temperature - self.gdd_base)

    def accumulate_chill(self, temperature: float, hours: float) -> float:
        """
        累积需冷量
        温度 < 7.2°C 时累积
        """
        if temperature < 7.2:
            return hours
        return 0.0

    def check_transition(self, next_phase: str) -> bool:
        """
        检查是否满足物候转换条件
        由积温驱动，非硬编码时间
        """
        required = self.gdd_requirements.get(next_phase)
        if required is None:
            return False
        return self.gdd_accumulated >= required
