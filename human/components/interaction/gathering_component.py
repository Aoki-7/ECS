#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:gathering_component.py
@说明:采集组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component

@dataclass(slots=True)
class GatheringComponent(Component):
    """
    采集组件 - 纯数据版
    存储采集技能和经验。
    """
    # 采集技能 {resource_type: skill_level}
    gathering_skills: Dict[str, float] = field(default_factory=dict)
    
    # 采集记录
    gathering_history: List[Dict] = field(default_factory=list)
    
    # 当前采集目标
    current_target: int = -1
    gathering_progress: float = 0.0
    
    # 采集效率
    efficiency: float = 1.0
    
    # 工具质量
    tool_quality: float = 1.0
