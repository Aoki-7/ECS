#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:poison_component.py
@说明:中毒组件
@时间:2026/03/19 11:25:04
@作者:Sherry
@版本:1.0
'''





# 已从 human/components/injury/poison_component.py 迁移至此
# 向后兼容导入: from human.components.injury.poison_component import PoisonComponent
from dataclasses import dataclass
from biology.components.injury.injury_component import InjuryComponent


@dataclass
class PoisonComponent(InjuryComponent):
    """
    中毒：持续伤害 + 可扩展debuff
    """
    damage_per_sec: float = 0.3