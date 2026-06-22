#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:gravity_component.py
@说明:重力组件 - 环境属性

重力是环境的一部分：
- 不同星球/环境有不同的重力加速度
- 影响物体下落、跳跃、物理碰撞
- 由 EnvironmentBuilder 配置，随环境变化
'''

from dataclasses import dataclass
from core.component import Component


@dataclass(slots=True)
class GravityComponent(Component):
    """
    重力组件 - 环境属性

    Attributes:
        acceleration: 重力加速度 m/s²（地球=9.8，月球=1.6）
        direction_x: 重力方向向量 x（默认 0）
        direction_y: 重力方向向量 y（默认 -1，向下）
        direction_z: 重力方向向量 z（默认 0）
        max_fall_speed: 最大下落速度（终端速度）
        is_enabled: 是否启用重力
    """
    acceleration: float = 9.8       # 重力加速度 m/s²
    direction_x: float = 0.0        # 方向向量 x
    direction_y: float = -1.0       # 方向向量 y（默认向下）
    direction_z: float = 0.0        # 方向向量 z
    max_fall_speed: float = 50.0    # 最大下落速度 m/s
    is_enabled: bool = True           # 是否启用

    def __post_init__(self):
        # 确保方向向量归一化
        import math
        length = math.sqrt(self.direction_x**2 + self.direction_y**2 + self.direction_z**2)
        if length > 0:
            self.direction_x /= length
            self.direction_y /= length
            self.direction_z /= length
