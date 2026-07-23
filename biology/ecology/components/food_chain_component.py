#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
食物链组件

标记实体在生态系统食物链中的位置，记录营养级和生态位信息。
"""

from dataclasses import dataclass, field
from core.component import Component


@dataclass(slots=True)
class FoodChainComponent(Component):
    """
    食物链位置组件

    Attributes:
        trophic_level: 营养级（1=生产者, 2=初级消费者, 3=次级消费者, 4=顶级捕食者）
        niche: 生态位类型（"producer", "herbivore", "carnivore", "omnivore", "scavenger"）
        energy_transfer_efficiency: 能量传递效率（0.0-1.0）
        prey_niches: 可捕食的niche列表
        predator_niches: 天敌niche列表
        biomass: 生物量（用于生态权重计算）
    """
    trophic_level: int = 1
    niche: str = "producer"
    energy_transfer_efficiency: float = 0.1
    prey_niches: list = field(default_factory=list)
    predator_niches: list = field(default_factory=list)
    biomass: float = 1.0