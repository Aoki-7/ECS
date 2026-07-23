#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:celestial_body_component.py
@说明:天体组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.component import Component

@dataclass(slots=True)
class CelestialBodyComponent(Component):
    """
    天体组件 - 纯数据版
    存储天体信息。
    """
    # 基本属性
    name: str = ""
    body_type: str = "star"
    mass: float = 7.342e22
    radius: float = 1.0
    
    # 轨道参数
    semi_major_axis: float = 1.0
    eccentricity: float = 0.0549
    inclination: float = 0.0
    
    # 当前位置
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # 相位
    phase: float = 0.0
    orbital_period: float = 27.32
    
    # 兼容性字段（兼容旧测试）
    body_name: str = "moon"
    distance: float = 3.844e8
    phase_rate: float = 0.0
    current_phase: float = 0.0
    orbital_eccentricity: float = 0.0549
    
    def __post_init__(self):
        """初始化后同步兼容性字段"""
        if self.body_name and not self.name:
            self.name = self.body_name
        if self.current_phase and not self.phase:
            self.phase = self.current_phase
        if self.orbital_eccentricity != 0.0549:
            self.eccentricity = self.orbital_eccentricity

    def to_dict(self) -> dict:
        """序列化"""
        return {
            'name': self.name,
            'body_type': self.body_type,
            'mass': self.mass,
            'radius': self.radius,
            'semi_major_axis': self.semi_major_axis,
            'eccentricity': self.eccentricity,
            'inclination': self.inclination,
            'position': self.position,
            'velocity': self.velocity,
            'phase': self.phase,
            'orbital_period': self.orbital_period,
            'body_name': self.body_name,
            'distance': self.distance,
            'phase_rate': self.phase_rate,
            'current_phase': self.current_phase,
            'orbital_eccentricity': self.orbital_eccentricity,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CelestialBodyComponent':
        """反序列化"""
        comp = cls()
        for key, value in data.items():
            if hasattr(comp, key):
                setattr(comp, key, value)
        return comp