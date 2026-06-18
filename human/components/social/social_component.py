#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:social_component.py
@说明:社交组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component

@dataclass(slots=True)
class SocialComponent(Component):
    """
    社交组件 - 纯数据版
    存储社交关系和冲突。
    """
    # 社交关系 {entity_id: relation_type}
    relations: Dict[int, str] = field(default_factory=dict)
    
    # 关系强度 {entity_id: strength}
    relation_strength: Dict[int, float] = field(default_factory=dict)
    
    # 冲突记录
    conflicts: List[Dict] = field(default_factory=list)
    
    # 社交状态
    is_socializing: bool = False
    current_interaction_partner: Optional[int] = None
    
    # 社交统计
    total_interactions: int = 0
    successful_interactions: int = 0
    failed_interactions: int = 0
