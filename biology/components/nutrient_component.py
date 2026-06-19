#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/nutrient_component.py
@说明:营养组件 - 纯数据版

存储生物实体的 N/P/K（氮/磷/钾）营养储备。
被 NutrientSystem 从环境吸收并消耗，被 DamageRepairSystem 间接影响（修复需要营养）。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class NutrientComponent(Component):
    """
    营养组件 - 纯数据

    Attributes:
        nitrogen: 氮储备。
        phosphorus: 磷储备。
        potassium: 钾储备。
        max_*: 各营养的上限。
    """

    nitrogen: float = 0.0
    phosphorus: float = 0.0
    potassium: float = 0.0
    max_nitrogen: float = 100.0
    max_phosphorus: float = 100.0
    max_potassium: float = 100.0

    @property
    def nitrogen_stress(self) -> float:
        """氮胁迫程度（0-1）"""
        if self.max_nitrogen <= 0:
            return 0.0
        return 1.0 - (self.nitrogen / self.max_nitrogen)

    @property
    def phosphorus_stress(self) -> float:
        """磷胁迫程度（0-1）"""
        if self.max_phosphorus <= 0:
            return 0.0
        return 1.0 - (self.phosphorus / self.max_phosphorus)

    @property
    def potassium_stress(self) -> float:
        """钾胁迫程度（0-1）"""
        if self.max_potassium <= 0:
            return 0.0
        return 1.0 - (self.potassium / self.max_potassium)

    # 兼容旧系统： nutrient_n / nutrient_p / nutrient_k 别名
    @property
    def nutrient_n(self) -> float:
        return self.nitrogen

    @nutrient_n.setter
    def nutrient_n(self, value: float) -> None:
        self.nitrogen = value

    @property
    def nutrient_p(self) -> float:
        return self.phosphorus

    @nutrient_p.setter
    def nutrient_p(self, value: float) -> None:
        self.phosphorus = value

    @property
    def nutrient_k(self) -> float:
        return self.potassium

    @nutrient_k.setter
    def nutrient_k(self, value: float) -> None:
        self.potassium = value

