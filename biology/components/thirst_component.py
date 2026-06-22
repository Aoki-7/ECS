#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:thirst_component.py
@说明:口渴需求组件 - 纯数据版
'''

from dataclasses import dataclass
from core.component import Component

@dataclass(slots=True)
class ThirstComponent(Component):
    """
    口渴需求组件 - 纯数据版
    
    Attributes:
        value: 口渴值 0-100 (0=不渴, 100=极度口渴)
        decay_rate: 每秒衰减率
        max_value: 最大值
    """
    value: float = 0.0          # 口渴值 0-100
    decay_rate: float = 0.8     # 每秒衰减率（比饥饿更快）
    max_value: float = 100.0    # 最大值
    
    def __post_init__(self):
        # 确保值在范围内
        self.value = max(0.0, min(self.value, self.max_value))
