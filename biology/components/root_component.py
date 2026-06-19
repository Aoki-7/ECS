#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根系组件

v3.2 新增 — P0

职责：
    - 存储植物根系数据
    - 记录根系深度、范围、密度
    - 支持水分和养分吸收

设计原则：
    - 纯数据组件，无业务逻辑
    - 根系参数因物种而异
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from core.component import Component


@dataclass
class RootComponent(Component):
    """
    根系组件

    Attributes:
        depth: 根系深度（米）
        spread: 根系水平扩展范围（米）
        density: 根系密度（0.0-1.0）
        water_absorption: 水分吸收能力（每 tick）
        nutrient_absorption: 养分吸收能力（每 tick）
        root_health: 根系健康度（0.0-1.0）
        mycorrhizal: 是否与菌根共生
    """

    depth: float = 1.0
    spread: float = 2.0
    density: float = 0.5
    water_absorption: float = 0.1
    nutrient_absorption: float = 0.05
    root_health: float = 1.0
    mycorrhizal: bool = False

    # 已占据的土壤网格（用于竞争计算）
    occupied_cells: set = field(default_factory=set)

    def to_dict(self) -> dict:
        return {
            "depth": self.depth,
            "spread": self.spread,
            "density": self.density,
            "water_absorption": self.water_absorption,
            "nutrient_absorption": self.nutrient_absorption,
            "root_health": self.root_health,
            "mycorrhizal": self.mycorrhizal,
            "occupied_cells": list(self.occupied_cells),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RootComponent":
        return cls(
            depth=data.get("depth", 1.0),
            spread=data.get("spread", 2.0),
            density=data.get("density", 0.5),
            water_absorption=data.get("water_absorption", 0.1),
            nutrient_absorption=data.get("nutrient_absorption", 0.05),
            root_health=data.get("root_health", 1.0),
            mycorrhizal=data.get("mycorrhizal", False),
            occupied_cells=set(data.get("occupied_cells", [])),
        )
