#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:light_scatter_component.py
@说明:大气光散射组件
@时间:2026/03/11 12:08:01
@作者:Sherry
@版本:1.0
'''




from dataclasses import dataclass

from core.component import Component

@dataclass
class LightScatterComponent(Component):
    """
    光散射
    """

    __slots__ = (
        "rayleigh_factor",
        "mie_factor",
        "cloud_attenuation",
    )

    def __init__(self):
        self.rayleigh_factor = 0.1
        self.mie_factor = 0.05
        self.cloud_attenuation = 0.0