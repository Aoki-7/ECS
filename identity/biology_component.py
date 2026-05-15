#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:biology_component.py
@说明:生物属性
@时间:2026/03/19 13:21:44
@作者:Sherry
@版本:1.0
'''

from core.component import Component

from dataclasses import dataclass

@dataclass
class BiologyComponent(Component):
    """
    生物属性

    Args:
        species: 种族
        gender: 性别
        age: 年龄
    """
    species: str = "Human"
    gender: str = "Unknown"
    age: float = 0.0
