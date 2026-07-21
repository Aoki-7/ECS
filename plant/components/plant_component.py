#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:plant_component.py
@说明:植物可收获属性组件
@时间:2026/06/01
@作者:AI Assistant
@版本:1.0
'''

from dataclasses import dataclass, field
from core.component import Component


@dataclass(slots=True)
class PlantComponent(Component):
    """
    植物可收获属性组件

    桥接植物生态与人类食物系统，标记植物的可收获属性。
    """
    # 当前可收获量（实时计算或缓存）
    harvestable_yield: float = 0.0

    # 最大产量潜力
    max_yield: float = 0.0

    # 可收获的生命周期阶段（默认 MATURE=3）
    harvest_stage: int = 3

    # 产出食物类型
    yield_type: str = "berry"

    # 单位营养值
    nutrition_per_unit: float = 5.0

    # 是否多年生（收获后是否保留实体）
    is_perennial: bool = True

    # 再生速率
    regrowth_rate: float = 0.1

    # 是否产出木材（乔木类）
    produces_wood: bool = False

    # 木材产量
    wood_amount: float = 0.0

    # ===== v3.3 新增：生理状态 =====
    # 健康度（0.0-1.0）
    health: float = 1.0

    # 水分（0.0-max_water）
    water: float = 50.0
    max_water: float = 100.0

    # 养分（0.0-max_nutrients）
    nutrients: float = 50.0
    max_nutrients: float = 100.0

    # 能量（光合作用积累）
    energy: float = 50.0
    max_energy: float = 100.0

    # ===== v4.16 新增：掉落标记 =====
    # 是否已掉落过资源，避免重复掉落
    dropped: bool = False

    def to_dict(self) -> dict:
        return {
            "harvestable_yield": self.harvestable_yield,
            "max_yield": self.max_yield,
            "harvest_stage": self.harvest_stage,
            "yield_type": self.yield_type,
            "nutrition_per_unit": self.nutrition_per_unit,
            "is_perennial": self.is_perennial,
            "regrowth_rate": self.regrowth_rate,
            "produces_wood": self.produces_wood,
            "wood_amount": self.wood_amount,
            "health": self.health,
            "water": self.water,
            "max_water": self.max_water,
            "nutrients": self.nutrients,
            "max_nutrients": self.max_nutrients,
            "energy": self.energy,
            "max_energy": self.max_energy,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlantComponent":
        return cls(
            harvestable_yield=data.get("harvestable_yield", 0.0),
            max_yield=data.get("max_yield", 0.0),
            harvest_stage=data.get("harvest_stage", 3),
            yield_type=data.get("yield_type", "berry"),
            nutrition_per_unit=data.get("nutrition_per_unit", 5.0),
            is_perennial=data.get("is_perennial", True),
            regrowth_rate=data.get("regrowth_rate", 0.1),
            produces_wood=data.get("produces_wood", False),
            wood_amount=data.get("wood_amount", 0.0),
            health=data.get("health", 1.0),
            water=data.get("water", 50.0),
            max_water=data.get("max_water", 100.0),
            nutrients=data.get("nutrients", 50.0),
            max_nutrients=data.get("max_nutrients", 100.0),
            energy=data.get("energy", 50.0),
            max_energy=data.get("max_energy", 100.0),
        )
