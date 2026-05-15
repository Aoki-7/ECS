#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:solar_position_component.py
@说明:太阳位置组件
@时间:2026/03/11 12:05:31
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass
class SolarPositionComponent(Component):
    """
    太阳位置
    """

    elevation: float = 0.0
    azimuth: float = 0.0
    day_length: float = 12.0