#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:temperature_component.py
@说明:体温组件
@时间:2026/03/21 22:04:04
@作者:Sherry
@版本:1.0
'''


from dataclasses import dataclass

from core.component import Component

@dataclass
class BodyTempComponent(Component):
    body_temp: float = 37.0
    optimal_temp: float = 37.0