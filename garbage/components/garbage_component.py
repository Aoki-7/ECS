#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:gabage_component.py
@说明:
@时间:2026/03/26 13:35:35
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component


@dataclass
class GarbageComponent(Component):
    """
    垃圾 / 腐败残留
    """
    toxicity: float = 0.2