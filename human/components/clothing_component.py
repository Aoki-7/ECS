#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
衣物组件

v3.0.1 新增 — P1

核心设计原则：
- 衣物保暖效果从材料属性自然计算
- 衣物耐久度从使用和磨损自然衰减
- 衣物知识从制作实践中积累
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component


@dataclass(slots=True)
class ClothingComponent(Component):
    """
    衣物组件

    记录单件衣物的属性和状态。
    """
    # 衣物类型
    clothing_type: str = "tunic"  # tunic, cloak, boots, hat

    # 材料类型
    material: str = "plant_fiber"  # plant_fiber, animal_hide, wool, leather

    # 保暖值 (°C 保护)
    insulation: float = 5.0

    # 覆盖身体部位
    coverage: List[str] = field(default_factory=lambda: ["torso"])

    # 耐久度 (0-1)
    durability: float = 1.0

    # 当前状态
    condition: str = "good"  # good, worn, damaged, ruined

    # 湿度 (0-1, 影响保暖效果)
    wetness: float = 0.0

    def calculate_effective_insulation(self) -> float:
        """计算有效保暖值"""
        base = self.insulation * self.durability
        # 湿衣物保暖效果降低
        wet_penalty = 1.0 - self.wetness * 0.7
        return base * wet_penalty

    def wear(self, amount: float = 0.01) -> None:
        """磨损"""
        self.durability = max(0.0, self.durability - amount)
        self._update_condition()

    def get_wet(self, amount: float = 0.1) -> None:
        """变湿"""
        self.wetness = min(1.0, self.wetness + amount)

    def dry(self, amount: float = 0.05) -> None:
        """晾干"""
        self.wetness = max(0.0, self.wetness - amount)

    def repair(self, amount: float = 0.2) -> None:
        """修复"""
        self.durability = min(1.0, self.durability + amount)
        self._update_condition()

    def _update_condition(self) -> None:
        """更新状态描述"""
        if self.durability > 0.7:
            self.condition = "good"
        elif self.durability > 0.4:
            self.condition = "worn"
        elif self.durability > 0.1:
            self.condition = "damaged"
        else:
            self.condition = "ruined"


@dataclass(slots=True)
class OutfitComponent(Component):
    """
    着装组件

    记录实体当前穿着的所有衣物。
    """
    # 穿着的衣物 (clothing_type -> entity_id)
    worn_items: Dict[str, int] = field(default_factory=dict)

    # 总保暖值
    total_insulation: float = 0.0

    def wear_item(self, clothing_id: int, clothing: ClothingComponent) -> None:
        """穿上衣物"""
        self.worn_items[clothing.clothing_type] = clothing_id
        self._recalculate_insulation()

    def remove_item(self, clothing_type: str) -> Optional[int]:
        """脱下衣物"""
        removed = self.worn_items.pop(clothing_type, None)
        self._recalculate_insulation()
        return removed

    def _recalculate_insulation(self) -> None:
        """重新计算总保暖值"""
        # 注意：这里只是占位，实际需要查询每个衣物的组件
        self.total_insulation = sum(
            5.0 for _ in self.worn_items.values()
        )

    def get_coverage(self) -> List[str]:
        """获取已覆盖的身体部位"""
        # 简化实现
        return ["torso"] if "tunic" in self.worn_items else []
