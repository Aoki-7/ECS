#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
气味组件

v3.0.3 新增 — P0

职责：
    - 存储实体的气味标记
    - 记录气味强度和类型
    - 支持气味衰减

设计原则：
    - 纯数据组件
    - 气味类型为字符串标签（可扩展）
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from core.component import Component


@dataclass
class SmellComponent(Component):
    """
    气味组件

    Attributes:
        scents: 气味字典 {气味类型: 强度}
        base_intensity: 基础气味强度（由物种决定）
        decay_rate: 气味衰减速率（每 tick）
        detection_radius: 可被检测的半径
    """

    scents: Dict[str, float] = field(default_factory=dict)
    base_intensity: float = 1.0
    decay_rate: float = 0.001
    detection_radius: float = 10.0

    # 特殊气味标记
    is_prey: bool = False  # 猎物气味（吸引捕食者）
    is_predator: bool = False  # 捕食者气味（驱赶猎物）
    is_mate: bool = False  # 配偶气味（吸引同类）
    is_territory: bool = False  # 领地气味（驱赶同类）

    def to_dict(self) -> dict:
        return {
            "scents": self.scents.copy(),
            "base_intensity": self.base_intensity,
            "decay_rate": self.decay_rate,
            "detection_radius": self.detection_radius,
            "is_prey": self.is_prey,
            "is_predator": self.is_predator,
            "is_mate": self.is_mate,
            "is_territory": self.is_territory,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SmellComponent":
        return cls(
            scents=data.get("scents", {}),
            base_intensity=data.get("base_intensity", 1.0),
            decay_rate=data.get("decay_rate", 0.001),
            detection_radius=data.get("detection_radius", 10.0),
            is_prey=data.get("is_prey", False),
            is_predator=data.get("is_predator", False),
            is_mate=data.get("is_mate", False),
            is_territory=data.get("is_territory", False),
        )