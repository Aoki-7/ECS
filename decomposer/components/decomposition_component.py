#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
DecompositionComponent — 分解状态组件

记录尸体分解过程中的详细状态，包括剩余养分和微生物活性。
由 DecomposerSystem 自动挂载到带有 CorpseComponent 的实体上。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class DecompositionComponent(Component):
    """
    分解状态组件

    Fields:
        remaining_nitrogen:    剩余氮含量
        remaining_phosphorus:  剩余磷含量
        remaining_potassium:   剩余钾含量
        remaining_organic_matter: 剩余有机质
        microbial_activity:    微生物活性 [0.0, 1.0]，受温度/湿度影响
        rate_multiplier:       分解速率倍率（默认 1.0）
        total_released:        已累计释放的养分总量（用于统计）
    """
    remaining_nitrogen: float = 0.0
    remaining_phosphorus: float = 0.0
    remaining_potassium: float = 0.0
    remaining_organic_matter: float = 0.0
    microbial_activity: float = 0.5
    rate_multiplier: float = 1.0
    total_released: float = 0.0
