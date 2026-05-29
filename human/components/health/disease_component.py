#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:disease_component.py
@说明:疾病组件
@时间:2026/05/29
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum, auto

from core.component import Component


class DiseaseType(Enum):
    INFECTIOUS = auto()       # 传染性疾病
    CHRONIC = auto()          # 慢性疾病
    ACUTE = auto()            # 急性病
    DEFICIENCY = auto()       # 营养缺乏症
    ENVIRONMENTAL = auto()    # 环境相关疾病


@dataclass
class DiseaseComponent(Component):
    """
    疾病组件
    存储实体当前患有的疾病列表和免疫状态
    """
    diseases: List[Dict] = field(default_factory=list)
    # 每项: {
    #   "name": str,
    #   "type": DiseaseType,
    #   "severity": float,      # 严重度 0-100
    #   "contagion": float,     # 传染性 0-1
    #   "duration": float,      # 总持续时间（小时），-1 表示永久
    #   "elapsed": float,       # 已持续时间
    #   "damage_rate": float    # 每秒对 hp 的伤害
    # }

    immunity: Dict[str, float] = field(default_factory=dict)
    # 疾病名 -> 免疫强度 0-1

    def has_disease(self, name: str) -> bool:
        return any(d["name"] == name for d in self.diseases)

    def add_disease(self, disease: Dict):
        if not self.has_disease(disease["name"]):
            self.diseases.append(disease)

    def remove_disease(self, name: str):
        self.diseases = [d for d in self.diseases if d["name"] != name]
