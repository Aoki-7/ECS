#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:injury_component.py
@说明:伤害基类组件
@时间:2026/03/19 11:19:48
@作者:Sherry
@版本:1.0
'''

from core.component import Component

from dataclasses import dataclass

@dataclass
class InjuryComponent(Component):
    """
        伤害基类组件（所有伤害的父类）

        Args:
            damage_per_sec: 每秒伤害
            duration: 持续时间（-1 表示永久）
            elapsed: 已经过时间
    """
    damage_per_sec: float = 0.0
    duration: float = -1.0
    elapsed: float = 0.0