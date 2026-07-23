#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:social_needs_component.py
@说明:社交需求组件 - 纯数据版
'''

from dataclasses import dataclass
from core.component import Component

@dataclass(slots=True)
class SocialNeedsComponent(Component):
    """
    社交需求组件 - 纯数据版
    
    Attributes:
        loneliness: 孤独感 0-100 (0=满足, 100=极度孤独)
        decay_rate: 每秒衰减率
        max_value: 最大值
    """
    loneliness: float = 0.0     # 孤独感 0-100
    decay_rate: float = 0.2     # 每秒衰减率（最慢）
    max_value: float = 100.0    # 最大值
    
    def __post_init__(self):
        # 确保值在范围内
        self.loneliness = max(0.0, min(self.loneliness, self.max_value))