#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:climate_oscillation_component.py
@说明:气候震荡组件
@时间:2026/03/14 11:16:25
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass
class ClimateOscillationComponent(Component):
    """
        支持厄尔尼诺-拉尼娜振荡，冰期等
    """
    oscillation_type: str = "ENSO"

    temperature_anomaly: float = 0.0
    precipitation_anomaly: float = 0.0

    wind_anomaly: float = 0.0
    pressure_anomaly: float = 0.0

    remaining_days: int = 0