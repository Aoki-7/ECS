#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水体组件

v3.5 新增 — P0

职责：
    - 存储河流、湖泊、湿地等水体的数据
    - 记录水量、流速、水质

设计原则：
    - 纯数据组件，无业务逻辑
    - 支持多种水体类型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.component import Component


@dataclass(slots=True)
class WaterBodyComponent(Component):
    """
    水体组件

    Attributes:
        body_type: 水体类型（river/lake/wetland/pond）
        volume: 水量（立方米）
        max_volume: 最大容量
        flow_rate: 流速（m³/s，河流用）
        inflow: 入流速率
        outflow: 出流速率
        evaporation: 蒸发速率
        pollution: 污染度（0.0-1.0）
        temperature: 水温
        depth: 平均深度（米）
        connected_to: 连接的水体ID列表（河流网络）
    """

    body_type: str = "pond"  # river/lake/wetland/pond
    volume: float = 1000.0
    max_volume: float = 10000.0
    flow_rate: float = 0.0
    inflow: float = 0.0
    outflow: float = 0.0
    evaporation: float = 0.0
    pollution: float = 0.0
    temperature: float = 20.0
    depth: float = 1.0
    connected_to: List[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "body_type": self.body_type,
            "volume": self.volume,
            "max_volume": self.max_volume,
            "flow_rate": self.flow_rate,
            "inflow": self.inflow,
            "outflow": self.outflow,
            "evaporation": self.evaporation,
            "pollution": self.pollution,
            "temperature": self.temperature,
            "depth": self.depth,
            "connected_to": self.connected_to.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WaterBodyComponent":
        return cls(
            body_type=data.get("body_type", "pond"),
            volume=data.get("volume", 1000.0),
            max_volume=data.get("max_volume", 10000.0),
            flow_rate=data.get("flow_rate", 0.0),
            inflow=data.get("inflow", 0.0),
            outflow=data.get("outflow", 0.0),
            evaporation=data.get("evaporation", 0.0),
            pollution=data.get("pollution", 0.0),
            temperature=data.get("temperature", 20.0),
            depth=data.get("depth", 1.0),
            connected_to=data.get("connected_to", []),
        )
