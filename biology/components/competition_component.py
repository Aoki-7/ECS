#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/competition_component.py
@说明:生态竞争组件

记录生物实体在生态系统中的竞争参数与结果。
被 CompetitionSystem 更新，被 GrowthSystem 间接影响（竞争结果写入 phenotype）。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass
class CompetitionComponent(Component):
    """
    生态竞争组件

    Attributes:
        canopy_radius: 冠层遮阴半径（格子），高大植株影响范围更大。
        root_radius: 根系竞争半径（格子），深根系争夺更多水分。
        competitive_ability: 竞争能力系数，基因决定的基础竞争力。
        light_competition_score: 光照竞争结果 (0~1)，越高表示处于越不利的遮阴环境。
        water_competition_score: 水分竞争结果 (0~1)，越高表示水分竞争越激烈。
    """

    canopy_radius: float = 1.0
    root_radius: float = 1.0
    competitive_ability: float = 1.0
    light_competition_score: float = 0.0
    water_competition_score: float = 0.0
