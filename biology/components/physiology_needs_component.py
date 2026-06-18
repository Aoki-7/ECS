#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:physiology_needs_component.py
@说明:生理需求组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component

@dataclass(slots=True)
class PhysiologyNeedsComponent(Component):
    """
    生理需求组件 - 纯数据版
    存储生理需求状态。
    """
    # 基本需求 (0-1)
    hunger: float = 0.0
    thirst: float = 0.0
    sleepiness: float = 0.0
    fatigue: float = 0.0
    
    # 精力/能量（兼容旧系统）
    energy: float = 100.0
    
    # 社交需求（兼容旧系统）
    social: float = 50.0
    
    # 最大需求值（兼容旧系统）
    max_hunger: float = 100.0
    max_thirst: float = 100.0
    max_energy: float = 100.0
    max_fatigue: float = 100.0
    max_comfort: float = 100.0
    max_social: float = 100.0
    
    # 舒适度
    comfort: float = 0.5
    temperature_comfort: float = 0.5
    
    # 卫生
    hygiene: float = 0.5
    cleanliness: float = 0.5
    
    # 健康
    health: float = 1.0
    pain: float = 0.0
    
    # 需求优先级
    priority_needs: List[str] = field(default_factory=list)
