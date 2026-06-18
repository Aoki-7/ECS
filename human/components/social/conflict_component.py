#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:conflict_component.py
@说明:冲突组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component

@dataclass(slots=True)
class ConflictComponent(Component):
    """
    冲突组件 - 纯数据版
    存储冲突信息。
    """
    # 活跃冲突 {entity_id: conflict_level}
    active_conflicts: Dict[int, float] = field(default_factory=dict)
    
    # 冲突历史
    conflict_history: List[Dict] = field(default_factory=list)
    
    # 当前冲突状态
    is_in_conflict: bool = False
    current_opponent: int = -1
    
    # 冲突统计
    total_conflicts: int = 0
    resolved_conflicts: int = 0
    escalated_conflicts: int = 0
