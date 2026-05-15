#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:solar_radiation_component.py
@说明:太阳辐射组件
@时间:2026/03/11 12:07:04
@作者:Sherry
@版本:1.0
'''




from dataclasses import dataclass

from core.component import Component

@dataclass
class SolarRadiationComponent(Component):
    """
    太阳辐射
    """

    __slots__ = (
        "solar_constant",      # 太阳常数 W/m^2
        "toa_radiation",       # 大气顶辐射
    )

    def __init__(self):
        self.solar_constant = 1361.0
        self.toa_radiation = 0.0