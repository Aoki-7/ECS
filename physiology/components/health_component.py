#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:health_component.py
@说明:生命值组件
@时间:2026/03/21 22:00:24
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass
class HealthComponent(Component):
    hp: float = 100.0
    max_hp: float = 100.0
    regen_rate: float = 0.5