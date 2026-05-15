#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:metabolism_component.py
@说明:代谢组件
@时间:2026/03/21 21:49:12
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component


@dataclass
class MetabolismComponent(Component):
    """
    代谢系统
    """
    basal_rate: float = 1.0          # 基础代谢率
    activity_multiplier: float = 1.0 # 行为影响