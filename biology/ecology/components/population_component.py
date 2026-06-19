#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
种群动态组件

记录种群参数，用于种群动态模型计算。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass(slots=True)
class PopulationComponent(Component):
    """
    种群动态参数

    Attributes:
        growth_rate: 内禀增长率 r（每时间步）
        carrying_capacity: 环境承载力 K
        population_density: 当前种群密度（实体数/面积）
        death_rate: 自然死亡率
        birth_rate: 出生率
        migration_rate: 迁移率（正=迁入，负=迁出）
    """
    growth_rate: float = 0.05
    carrying_capacity: float = 100.0
    population_density: float = 0.0
    death_rate: float = 0.01
    birth_rate: float = 0.0
    migration_rate: float = 0.0
