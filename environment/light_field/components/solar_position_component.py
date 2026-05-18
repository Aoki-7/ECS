#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:solar_position_component.py
@说明:太阳位置组件
@时间:2026/05/17
@作者:Sherry
@版本:2.0
'''

from dataclasses import dataclass

from core.component import Component


@dataclass
class SolarPositionComponent(Component):
    """
    太阳位置组件

    elevation:   太阳高度角 (°)，0=地平线, 90=天顶。夜间 ≤ 0
    azimuth:     太阳方位角 (°)，从北顺时针，0=北, 90=东, 180=南, 270=西
    day_length:  昼长 (h)，当前日期的理论日照小时数
    is_night:    是否夜间（elevation ≤ 0）
    latitude:    纬度 (°)，北正南负，用于计算太阳位置
    """

    elevation: float = 0.0
    azimuth: float = 0.0
    day_length: float = 12.0
    is_night: bool = True
    latitude: float = 35.0
