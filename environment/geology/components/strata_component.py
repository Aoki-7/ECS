#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地层组件

v3.5 新增 — P0

职责：
    - 存储地下地质结构
    - 记录岩层、土壤层、矿床

设计原则：
    - 纯数据组件，无业务逻辑
    - 支持多层地层
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component


@dataclass
class StrataComponent(Component):
    """
    地层组件

    Attributes:
        layers: 地层列表 [{depth, type, hardness, mineral}]
        bedrock_depth: 基岩深度（米）
        fault_lines: 断层线列表
        mineral_deposits: 矿床 {矿物类型: 储量}
    """

    layers: List[Dict] = field(default_factory=list)
    bedrock_depth: float = 10.0
    fault_lines: List[Dict] = field(default_factory=list)
    mineral_deposits: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "layers": self.layers.copy(),
            "bedrock_depth": self.bedrock_depth,
            "fault_lines": self.fault_lines.copy(),
            "mineral_deposits": self.mineral_deposits.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StrataComponent":
        return cls(
            layers=data.get("layers", []),
            bedrock_depth=data.get("bedrock_depth", 10.0),
            fault_lines=data.get("fault_lines", []),
            mineral_deposits=data.get("mineral_deposits", {}),
        )