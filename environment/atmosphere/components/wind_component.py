#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
风场组件 v4.16.0
存储每个网格单元的风属性，参与大气输送过程
"""

from dataclasses import dataclass
from enum import Enum, auto
from core.component import Component
import math


class WindDirection(Enum):
    """风向枚举"""
    N = auto()    # 北
    NE = auto()   # 东北
    E = auto()    # 东
    SE = auto()   # 东南
    S = auto()    # 南
    SW = auto()   # 西南
    W = auto()    # 西
    NW = auto()   # 西北
    CALM = auto() # 无风


@dataclass(slots=True)
class WindComponent(Component):
    """
    风场组件
    每个环境网格单元挂载，存储风速、风向等风属性
    """
    
    # 风速（m/s）
    speed: float = 2.0
    # 风向（角度，0°=北，顺时针旋转）
    direction: float = 0.0
    # 阵风系数（0-1），风速波动幅度
    gust_factor: float = 0.2
    # 边界层高度（m）
    boundary_layer_height: float = 1000.0
    
    @property
    def direction_enum(self) -> WindDirection:
        """获取风向枚举值"""
        if self.speed < 0.5:
            return WindDirection.CALM
        
        # 角度归一化到0-360
        dir_norm = self.direction % 360
        if dir_norm < 22.5 or dir_norm >= 337.5:
            return WindDirection.N
        elif dir_norm < 67.5:
            return WindDirection.NE
        elif dir_norm < 112.5:
            return WindDirection.E
        elif dir_norm < 157.5:
            return WindDirection.SE
        elif dir_norm < 202.5:
            return WindDirection.S
        elif dir_norm < 247.5:
            return WindDirection.SW
        elif dir_norm < 292.5:
            return WindDirection.W
        else:
            return WindDirection.NW
    
    @property
    def u_component(self) -> float:
        """风的东向分量（u，正为东）"""
        return self.speed * math.sin(math.radians(self.direction))
    
    @property
    def v_component(self) -> float:
        """风的北向分量（v，正为北）"""
        return self.speed * math.cos(math.radians(self.direction))
    
    def get_wind_effect(self, area: float = 1.0) -> float:
        """计算风力作用效果，用于种子传播、建筑受力等"""
        # 风压公式：0.5 * 空气密度 * 风速² * 面积
        air_density = 1.225  # kg/m³
        return 0.5 * air_density * self.speed**2 * area
    
    def get_transport_distance(self, time: float, height: float = 1.0) -> float:
        """计算颗粒物在风中的输送距离"""
        # 高度小于边界层时，风速随高度对数增加
        if height < self.boundary_layer_height:
            height_factor = math.log(height / 0.01) / math.log(10 / 0.01)  # 10m高度为基准
        else:
            height_factor = 1.0
        
        return self.speed * height_factor * time
