#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:hunger_component.py
@说明:饥饿需求组件 - 纯数据版
'''

from dataclasses import dataclass
from core.component import Component

@dataclass(slots=True)
class HungerComponent(Component):
    """
    饥饿需求组件 - 纯数据版
    
    Attributes:
        value: 饥饿值 0-100 (0=饱食, 100=极度饥饿)
        decay_rate: 每秒衰减率
        max_value: 最大值
    """
    value: float = 0.0          # 饥饿值 0-100
    decay_rate: float = 0.5     # 每秒衰减率
    max_value: float = 100.0    # 最大值
    
    def __post_init__(self):
        # 确保值在范围内
        self.value = max(0.0, min(self.value, self.max_value))