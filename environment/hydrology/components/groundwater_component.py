#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地下水组件

v3.5 新增 — P0

职责：
    - 存储地下水含水层数据
    - 记录水位、渗透性、水质

设计原则：
    - 纯数据组件，无业务逻辑
    - 与土壤系统交互
"""

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component


@dataclass(slots=True)
class GroundwaterComponent(Component):
    """
    地下水组件

    Attributes:
        aquifer_type: 含水层类型（confined/unconfined）
        water_table: 地下水位（米，相对于地表）
        porosity: 孔隙度（0.0-1.0）
        permeability: 渗透系数（m/day）
        recharge_rate: 补给速率（mm/day）
        extraction: 抽取速率（m³/day）
        pollution: 污染度（0.0-1.0）
        salinity: 盐度（ppm）
    """

    aquifer_type: str = "unconfined"
    water_table: float = -5.0  # 地下5米
    porosity: float = 0.3
    permeability: float = 1.0
    recharge_rate: float = 0.0
    extraction: float = 0.0
    pollution: float = 0.0
    salinity: float = 0.0

    def to_dict(self) -> dict:
        return {
            "aquifer_type": self.aquifer_type,
            "water_table": self.water_table,
            "porosity": self.porosity,
            "permeability": self.permeability,
            "recharge_rate": self.recharge_rate,
            "extraction": self.extraction,
            "pollution": self.pollution,
            "salinity": self.salinity,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GroundwaterComponent":
        return cls(
            aquifer_type=data.get("aquifer_type", "unconfined"),
            water_table=data.get("water_table", -5.0),
            porosity=data.get("porosity", 0.3),
            permeability=data.get("permeability", 1.0),
            recharge_rate=data.get("recharge_rate", 0.0),
            extraction=data.get("extraction", 0.0),
            pollution=data.get("pollution", 0.0),
            salinity=data.get("salinity", 0.0),
        )
