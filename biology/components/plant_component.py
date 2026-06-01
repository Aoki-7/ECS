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


@dataclass
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
