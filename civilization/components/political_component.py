#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:political_component.py
@说明:政治组件 - 纯数据版

政治属性：
- power: 权力等级
- faction: 派系归属
- laws: 制定/遵守的法律
- diplomacy: 外交关系
- governance: 治理方式
'''

from dataclasses import dataclass, field
from typing import Dict, List, Any

from core.component import Component


@dataclass(slots=True)
class PoliticalComponent(Component):
    """
    政治组件 - 纯数据版

    Attributes:
        power_level: 权力等级 [0.0, 1.0]
        faction_id: 派系 ID
        faction_name: 派系名称
        laws: 法律列表
        diplomatic_relations: 外交关系 {entity_id: relation_value}
        governance_style: 治理方式（autocracy/democracy/oligarchy/anarchy）
        influence: 影响力 [0.0, 1.0]
        loyalty: 忠诚度 [0.0, 1.0]
    """
    power_level: float = 0.0
    faction_id: int = 0
    faction_name: str = "neutral"
    laws: List[str] = field(default_factory=list)
    diplomatic_relations: Dict[int, float] = field(default_factory=dict)
    governance_style: str = "anarchy"
    influence: float = 0.0
    loyalty: float = 0.5

    def __post_init__(self):
        # 限制数值范围
        self.power_level = max(0.0, min(1.0, self.power_level))
        self.influence = max(0.0, min(1.0, self.influence))
        self.loyalty = max(0.0, min(1.0, self.loyalty))