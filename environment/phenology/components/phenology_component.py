#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:phenology_component.py
@说明:物候组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component

@dataclass(slots=False)
class PhenologyComponent(Component):
    """
    物候组件 - 纯数据版
    存储物候信息。
    """
    # 生长度日
    gdd: float = 0.0
    base_temperature: float = 10.0
    
    # 需冷量
    chill_hours: float = 0.0
    chill_requirement: float = 1000.0
    
    # 物候阶段
    current_stage: str = "dormant"
    stage_progress: float = 0.0
    
    # 历史记录
    phenology_history: List[Dict] = field(default_factory=list)
    
    # 触发条件
    gdd_threshold: float = 100.0
    chill_threshold: float = 500.0
    
    # 兼容性字段（兼容旧测试）
    phenophase: str = "dormant"
    gdd_base: float = 5.0
    gdd_accumulated: float = 0.0
    day_length_sensitivity: float = 1.0
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            'phenophase': self.phenophase,
            'gdd_accumulated': self.gdd_accumulated,
            'chill_hours': self.chill_hours,
            'gdd_base': self.gdd_base,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PhenologyComponent':
        """反序列化"""
        comp = cls()
        for key, value in data.items():
            if hasattr(comp, key):
                setattr(comp, key, value)
        return comp
    
    def __getattr__(self, name: str):
        """动态返回默认值"""
        return 0.0