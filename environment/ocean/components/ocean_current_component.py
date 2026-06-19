#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
洋流组件

v3.5 新增 — P1

职责：
    - 存储洋流数据
    - 记录流速、方向、温度

设计原则：
    - 纯数据组件，无业务逻辑
    - 支持暖流/寒流
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.component import Component


@dataclass
class OceanCurrentComponent(Component):
    """
    洋流组件

    Attributes:
        current_type: 洋流类型（warm/cold）
        velocity: 流速向量 (vx, vy)
        temperature: 水温
        salinity: 盐度（ppt）
        depth: 深度层（surface/intermediate/deep）
        connected_to: 连接的洋流ID列表
    """

    current_type: str = "warm"  # warm/cold
    velocity: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    temperature: float = 20.0
    salinity: float = 35.0  # ppt
    depth: str = "surface"  # surface/intermediate/deep
    connected_to: List[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "current_type": self.current_type,
            "velocity": list(self.velocity),
            "temperature": self.temperature,
            "salinity": self.salinity,
            "depth": self.depth,
            "connected_to": self.connected_to.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OceanCurrentComponent":
        return cls(
            current_type=data.get("current_type", "warm"),
            velocity=tuple(data.get("velocity", [0.0, 0.0])),
            temperature=data.get("temperature", 20.0),
            salinity=data.get("salinity", 35.0),
            depth=data.get("depth", "surface"),
            connected_to=data.get("connected_to", []),
        )
