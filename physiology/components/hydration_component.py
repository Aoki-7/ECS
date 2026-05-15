#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:hydration_component.py
@说明:体液组件
@时间:2026/03/21 21:52:48
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component


@dataclass
class HydrationComponent(Component):
    water_level: float = 100.0
    dehydration_rate: float = 0.1