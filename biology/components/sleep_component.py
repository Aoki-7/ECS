#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:sleep_component.py
@说明:睡眠需求组件 - 纯数据版
'''

from dataclasses import dataclass
from core.component import Component

@dataclass(slots=True)
class SleepComponent(Component):
    """
    睡眠需求组件 - 纯数据版
    
    Attributes:
        value: 困倦值 0-100 (0=清醒, 100=极度困倦)
        decay_rate: 每秒衰减率
        max_value: 最大值
        is_sleeping: 是否正在睡眠
    """
    value: float = 0.0          # 困倦值 0-100
    decay_rate: float = 0.3     # 每秒衰减率（较慢）
    max_value: float = 100.0    # 最大值
    is_sleeping: bool = False   # 是否正在睡眠
    
    def __post_init__(self):
        # 确保值在范围内
        self.value = max(0.0, min(self.value, self.max_value))