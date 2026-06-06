#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:disease_component.py
@说明:疾病组件
@时间:2026/05/29
@版本:1.0
'''

# 已从 human/components/health/disease_component.py 迁移至此
# 向后兼容导入: from human.components.health.disease_component import DiseaseComponent, DiseaseType
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum, auto

from core.component import Component


class DiseaseType(Enum):
    INFECTIOUS = auto()       # 传染性疾病
    CHRONIC = auto()          # 慢性疾病
    ACUTE = auto()            # 急性病
    DEFICIENCY = auto()       # 营养缺乏症
    ENVIRONMENTAL = auto()    # 环境相关疾病


@dataclass(slots=True)
class DiseaseRecord:
    """单条疾病记录（类型化替代 Dict）"""
    name: str
    type: DiseaseType
    severity: float = 0.0       # 严重度 0-100
    contagion: float = 0.0      # 传染性 0-1
    duration: float = -1.0      # 总持续时间（小时），-1 表示永久
    elapsed: float = 0.0        # 已持续时间
    damage_rate: float = 0.0    # 每秒对 hp 的伤害

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type.name,
            "severity": self.severity,
            "contagion": self.contagion,
            "duration": self.duration,
            "elapsed": self.elapsed,
            "damage_rate": self.damage_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DiseaseRecord":
        return cls(
            name=data["name"],
            type=DiseaseType[data.get("type", "CHRONIC")],
            severity=data.get("severity", 0.0),
            contagion=data.get("contagion", 0.0),
            duration=data.get("duration", -1.0),
            elapsed=data.get("elapsed", 0.0),
            damage_rate=data.get("damage_rate", 0.0),
        )


@dataclass(slots=True)
class DiseaseComponent(Component):
    """
    疾病组件
    存储实体当前患有的疾病列表和免疫状态
    """
    diseases: List[DiseaseRecord] = field(default_factory=list)
    immunity: Dict[str, float] = field(default_factory=dict)
    # 疾病名 -> 免疫强度 0-1

    def has_disease(self, name: str) -> bool:
        return any(d.name == name for d in self.diseases)

    def add_disease(self, disease: DiseaseRecord):
        if not self.has_disease(disease.name):
            self.diseases.append(disease)

    def remove_disease(self, name: str):
        self.diseases = [d for d in self.diseases if d.name != name]

    def get_disease(self, name: str) -> Optional[DiseaseRecord]:
        for d in self.diseases:
            if d.name == name:
                return d
        return None
