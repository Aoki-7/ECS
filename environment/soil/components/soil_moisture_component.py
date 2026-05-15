#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:soil_moisture_component.py
@说明:土壤水分
@时间:2026/03/09 09:29:38
@作者:Sherry
@版本:1.0
'''




from dataclasses import dataclass

from core.component import Component

@dataclass
class SoilMoistureComponent(Component):
    """
    土壤水分
    """
    moisture: float = 0.5   # 当前土壤湿度 0-1
    capacity: float = 1.0   # 最大持水能力