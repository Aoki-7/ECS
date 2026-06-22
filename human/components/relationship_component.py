#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:relationship_component.py
@说明:关系组件 - 纯数据版

关系类型：
- friendly: 友好度 [-1.0, 1.0]
- trust: 信任度 [-1.0, 1.0]
- respect: 尊重度 [-1.0, 1.0]
- intimacy: 亲密度 [-1.0, 1.0]
- rivalry: 竞争度 [-1.0, 1.0]

关系状态：
- friend: 朋友
- enemy: 敌人
- neutral: 中立
- family: 家人
- lover: 恋人
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component


@dataclass(slots=True)
class RelationshipComponent(Component):
    """
    关系组件 - 纯数据版

    Attributes:
        target_entity_id: 关系目标实体 ID
        friendly: 友好度 [-1.0, 1.0]
        trust: 信任度 [-1.0, 1.0]
        respect: 尊重度 [-1.0, 1.0]
        intimacy: 亲密度 [-1.0, 1.0]
        rivalry: 竞争度 [-1.0, 1.0]
        status: 关系状态（friend/enemy/neutral/family/lover）
        history: 关系历史事件列表
    """
    target_entity_id: int = 0
    friendly: float = 0.0
    trust: float = 0.0
    respect: float = 0.0
    intimacy: float = 0.0
    rivalry: float = 0.0
    status: str = "neutral"
    history: List[str] = field(default_factory=list)

    def __post_init__(self):
        # 限制所有值在 [-1.0, 1.0] 范围内
        for attr in ['friendly', 'trust', 'respect', 'intimacy', 'rivalry']:
            value = getattr(self, attr)
            setattr(self, attr, max(-1.0, min(1.0, value)))
