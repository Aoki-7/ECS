#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:combat_stats_component.py
@说明:战斗属性组件
@时间:2026/05/29
@版本:1.0
'''

from dataclasses import dataclass
from core.component import Component


@dataclass
class CombatStatsComponent(Component):
    """
    战斗属性组件
    存储实体的战斗相关数值
    """
    attack_power: float = 10.0       # 攻击力
    defense_power: float = 5.0       # 防御力
    attack_range: float = 1.5        # 攻击范围（格）
    aggression: float = 0.5          # 侵略性 0-1
