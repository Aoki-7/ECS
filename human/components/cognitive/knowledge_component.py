#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:knowledge_component.py
@说明:知识组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from core.component import Component

@dataclass(slots=True)
class KnowledgeComponent(Component):
    """
    知识组件 - 纯数据版
    存储技术和文化知识。
    """
    # 已知技术
    known_technologies: Set[str] = field(default_factory=set)
    
    # 技能知识 {skill_name: level}
    skill_knowledge: Dict[str, float] = field(default_factory=dict)
    
    # 文化事实
    cultural_facts: List[str] = field(default_factory=list)
    
    # 经验教训
    lessons: List[Dict] = field(default_factory=list)
    
    # 知识来源
    knowledge_sources: Dict[str, str] = field(default_factory=dict)
