#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:body_component.py
@说明:
@时间:2026/03/13 11:10:55
@作者:Sherry
@版本:1.0
'''
from dataclasses import dataclass

from core.component import Component

@dataclass
class BodyComponent(Component):
    """
        身体组件
        Args:
            height: 身高
            weight: 体重
            strength: 力量
            agility: 敏捷
            endurance: 耐力
    """
    height: float
    weight: float
    strength: float=1.0
    agility: float=1.0
    endurance: float=1.0