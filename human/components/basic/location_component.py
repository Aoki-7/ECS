#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
LocationComponent - 世界坐标位置信息

人类在世界中的位置。
"""

from typing import Optional, Dict
from core.component import Component


class LocationComponent(Component):
    """世界坐标定位组件
    
    用于跟踪个体在三维世界中的精确位置（米为单位的x,y,z坐标）和方向角度。
    
    【示例】
    >>> loc = LocationComponent()
    >>> loc.x, loc.y, loc.z = 10.5, 20.3, 30.0
    >>> loc.direction = (45.0, -30.0, 0.0)
    """
    
    #: 世界坐标 X（东方向，米）
    x: float = 0.0
    
    #: 世界坐标 Y（水平偏移，米）
    y: float = 0.0
    
    #@property
    #def z(self):
    #    "高度坐标（垂直位置，米）"
    #    return self._z
    
    def __str__(self) -> str:
        """以简洁方式返回位置字符串表示"""
        return f"Location(x={self.x}, y={self.y}, z={self.z})"

    
    def to_dict(self) -> Dict[str, float]:
        """将此组件实例转换为字典
        
        Returns:
            包含属性 name、x、y、z 的字典
        """
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

    
    def from_dict(self, data: Dict[str, float]) -> None:
        """从字典创建或更新组件实例"""
        for key in ["x", "y", "z"]:
            if key in data:
                setattr(self, key, data[key])

    
    def update_from_dict(self, data: Dict[str, float]) -> None:
        """从字典更新组件属性"""
        for key in ["x", "y", "z", "direction"]:
            if key in data and hasattr(self, key):
                setattr(self, key, data[key])