#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
污染组件

v3.5 新增 — P1

职责：
    - 存储空气/水/土壤污染度
    - 记录污染物类型和浓度

设计原则：
    - 纯数据组件，无业务逻辑
    - 支持多种污染类型
"""

from dataclasses import dataclass, field
from typing import Dict

from core.component import Component


@dataclass
class PollutionComponent(Component):
    """
    污染组件

    Attributes:
        air_pollution: 空气污染度 (0.0-1.0)
        water_pollution: 水污染度 (0.0-1.0)
        soil_pollution: 土壤污染度 (0.0-1.0)
        pollutants: 污染物浓度 {类型: ppm}
        source: 污染源类型 (industrial/agricultural/natural)
    """

    air_pollution: float = 0.0
    water_pollution: float = 0.0
    soil_pollution: float = 0.0
    pollutants: Dict[str, float] = field(default_factory=dict)
    source: str = "natural"

    def to_dict(self) -> dict:
        return {
            "air_pollution": self.air_pollution,
            "water_pollution": self.water_pollution,
            "soil_pollution": self.soil_pollution,
            "pollutants": self.pollutants.copy(),
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PollutionComponent":
        return cls(
            air_pollution=data.get("air_pollution", 0.0),
            water_pollution=data.get("water_pollution", 0.0),
            soil_pollution=data.get("soil_pollution", 0.0),
            pollutants=data.get("pollutants", {}),
            source=data.get("source", "natural"),
        )