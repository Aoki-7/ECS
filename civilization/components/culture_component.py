#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:culture_component.py
@说明:文化组件 - 纯数据版

文化属性：
- language: 语言
- religion: 宗教信仰
- traditions: 传统习俗
- art: 艺术形式
- knowledge: 知识传承
'''

from dataclasses import dataclass, field
from typing import Dict, List, Any

from core.component import Component


@dataclass(slots=True)
class CultureComponent(Component):
    """
    文化组件 - 纯数据版

    Attributes:
        language: 语言
        religion: 宗教信仰
        traditions: 传统习俗列表
        art_forms: 艺术形式列表
        knowledge: 知识字典 {topic: level}
        customs: 习俗列表
        festivals: 节日列表
        cultural_identity: 文化认同度 [0.0, 1.0]
    """
    language: str = "common"
    religion: str = "none"
    traditions: List[str] = field(default_factory=list)
    art_forms: List[str] = field(default_factory=list)
    knowledge: Dict[str, float] = field(default_factory=dict)
    customs: List[str] = field(default_factory=list)
    festivals: List[str] = field(default_factory=list)
    cultural_identity: float = 0.5

    def __post_init__(self):
        # 限制数值范围
        self.cultural_identity = max(0.0, min(1.0, self.cultural_identity))
        # 限制知识等级
        for topic, level in self.knowledge.items():
            self.knowledge[topic] = max(0.0, min(1.0, level))
