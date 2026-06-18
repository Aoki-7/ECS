#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:solar_position_component.py
@说明:太阳位置组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass

from core.component import Component

@dataclass(slots=True)
class SolarPositionComponent(Component):
    """
    太阳位置组件 - 纯数据版
    存储太阳位置信息。
    """
    # 位置角度
    azimuth: float = 0.0
    elevation: float = 0.0
    
    # 时间相关
    sunrise_time: float = 6.0
    sunset_time: float = 18.0
    day_length: float = 12.0
    
    # 状态
    is_daytime: bool = True
    is_twilight: bool = False
    
    # 光照强度
    light_intensity: float = 1.0
    uv_index: float = 0.0
