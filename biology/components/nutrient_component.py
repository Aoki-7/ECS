#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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