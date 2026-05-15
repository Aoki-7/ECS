#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:disease_component.py
@说明:疾病组件
@时间:2026/03/21 22:15:17
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass
class DiseaseComponent(Component):
    infection_level: float = 0.0