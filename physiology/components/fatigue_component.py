#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:fatigue_component.py
@说明:疲劳系统，与能量系统独立
@时间:2026/03/21 22:06:04
@作者:Sherry
@版本:1.0
'''

# energy 不等于 fatigue

from dataclasses import dataclass

from core.component import Component


@dataclass
class FatigueComponent(Component):
    fatigue: float = 0.0
    recovery_rate: float = 0.2