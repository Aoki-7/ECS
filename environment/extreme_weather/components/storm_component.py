#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:storm_component.py
@说明:风暴组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component

@dataclass(slots=False)
class StormComponent(Component):
    """
    风暴组件 - 纯数据版
    存储风暴信息。
    """
    # 基本属性
    storm_type: str = "thunderstorm"
    intensity: float = 0.0
    
    # 位置
    center_x: float = 0.0
    center_y: float = 0.0
    radius: float = 0.0
    
    # 运动
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    
    # 物理参数
    pressure_gradient: float = 0.0
    coriolis_force: float = 0.0
    wind_speed: float = 0.0
    
    # 生命周期
    age: float = 0.0
    max_age: float = 100.0
    is_active: bool = True
    
    # 兼容性字段
    central_pressure: float = 1013.0
    latitude: float = 0.0
    longitude: float = 0.0
    max_wind_speed: float = 0.0
    eye_diameter: float = 0.0
    outer_radius: float = 0.0
    movement_speed: float = 0.0
    movement_direction: float = 0.0
    lifetime: float = 0.0
    max_lifetime: float = 100.0
    temperature_gradient: float = 0.0
    diameter: float = 0.0
    humidity: float = 0.5
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            'storm_type': self.storm_type,
            'intensity': self.intensity,
            'center_x': self.center_x,
            'center_y': self.center_y,
            'radius': self.radius,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'central_pressure': self.central_pressure,
            'max_wind_speed': self.max_wind_speed,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StormComponent':
        """反序列化"""
        comp = cls()
        for key, value in data.items():
            if hasattr(comp, key):
                setattr(comp, key, value)
        return comp
    
    def __getattr__(self, name: str):
        """动态返回默认值"""
        return 0.0
