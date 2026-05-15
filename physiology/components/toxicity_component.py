#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:toxicity_component.py
@说明:毒素组件
@时间:2026/03/21 22:11:42
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass
class ToxicityComponent(Component):
    toxin_level: float = 0.0
    decay_rate: float = 0.05