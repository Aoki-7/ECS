#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:bleeding_component.py
@说明:流血伤害组件
@时间:2026/03/19 11:24:07
@作者:Sherry
@版本:1.0
'''

# 已从 human/components/injury/bleeding_component.py 迁移至此
# 向后兼容导入: from human.components.injury.bleeding_component import BleedingComponent
from dataclasses import dataclass
from biology.components.injury.injury_component import InjuryComponent


@dataclass
class BleedingComponent(InjuryComponent):
    """
    流血：持续掉血
    """
    damage_per_sec: float = 0.5