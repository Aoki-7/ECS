#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主观记忆：MemoryInstance

某主体对某概念的具体记忆。
个性化、可能扭曲、可能遗忘。
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum, auto

from .sensory_description import SensoryDescription
from .emotional_tag import EmotionalTag
from .association_link import AssociationLink


class SubjectType(Enum):
    """主体类型（当前限定动物/人类）"""
    ANIMAL = auto()
    HUMAN = auto()


@dataclass
class MemoryInstance:
    """
    主观记忆 = 某主体对某概念的具体记忆

    类似数据库"观点表"中的一条记录。
    多个 MemoryInstance 可以指向同一个 Concept。
    """
    memory_id: str                     # 唯一标识
    concept_id: str                    # 关联的客观概念
    subject_id: int                    # 记忆主体（实体ID）
    subject_type: SubjectType          # 主体类型

    # === 主观感官印象（结构化，可能缺失/扭曲）===
    sensory_impression: SensoryDescription = field(default_factory=SensoryDescription)

    # === 情感 ===
    emotional_tag: EmotionalTag = field(default_factory=EmotionalTag)

    # === 记忆质量 ===
    confidence: float = 1.0            # 确信度 0.0~1.0
    distortion_level: float = 0.0      # 扭曲度 0.0~1.0（与客观描述的偏差）
    clarity: float = 1.0               # 清晰度 0.0~1.0（随时间衰减）

    # === 联想网络 ===
    associations: List[AssociationLink] = field(default_factory=list)

    # === 叙事 ===
    narrative: Optional[str] = None    # "那天我踢了它，摔倒了"

    # === 时间 ===
    first_contact: float = 0.0         # 首次接触时间
    last_recall: float = 0.0           # 上次回忆时间
    recall_count: int = 0              # 回忆次数

    # === 来源 ===
    formation_type: str = "direct"     # "direct"直接体验 / "narrative"间接听闻
    source_subject_id: Optional[int] = None  # 若间接听闻，信息来源主体

    def decay(self, rate: float = 0.01) -> None:
        """记忆自然衰减"""
        self.clarity = max(0.0, self.clarity - rate)
        self.confidence = max(0.0, self.confidence - rate * 0.5)

    def recall(self, timestamp: float) -> None:
        """被回忆一次，更新统计"""
        self.last_recall = timestamp
        self.recall_count += 1
        # 回忆可能增强清晰度（但不超过原始值）
        self.clarity = min(1.0, self.clarity + 0.05)

    def calculate_importance(self) -> float:
        """
        计算记忆重要性。
        用于遗忘决策：重要性低的记忆优先遗忘。
        """
        emotional_weight = self.emotional_tag.intensity * 0.4
        clarity_weight = self.clarity * 0.2
        recall_weight = min(1.0, self.recall_count / 10) * 0.2
        confidence_weight = self.confidence * 0.2
        return emotional_weight + clarity_weight + recall_weight + confidence_weight

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "memory_id": self.memory_id,
            "concept_id": self.concept_id,
            "subject_id": self.subject_id,
            "subject_type": self.subject_type.name,
            "sensory_impression": self.sensory_impression.to_dict(),
            "emotional_tag": self.emotional_tag.to_dict(),
            "confidence": self.confidence,
            "distortion_level": self.distortion_level,
            "clarity": self.clarity,
            "associations": [a.to_dict() for a in self.associations],
            "narrative": self.narrative,
            "first_contact": self.first_contact,
            "last_recall": self.last_recall,
            "recall_count": self.recall_count,
            "formation_type": self.formation_type,
            "source_subject_id": self.source_subject_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryInstance":
        """从字典反序列化"""
        return cls(
            memory_id=data["memory_id"],
            concept_id=data["concept_id"],
            subject_id=data["subject_id"],
            subject_type=SubjectType[data["subject_type"]],
            sensory_impression=SensoryDescription.from_dict(data["sensory_impression"]),
            emotional_tag=EmotionalTag.from_dict(data["emotional_tag"]),
            confidence=data.get("confidence", 1.0),
            distortion_level=data.get("distortion_level", 0.0),
            clarity=data.get("clarity", 1.0),
            associations=[AssociationLink.from_dict(a) for a in data.get("associations", [])],
            narrative=data.get("narrative"),
            first_contact=data.get("first_contact", 0.0),
            last_recall=data.get("last_recall", 0.0),
            recall_count=data.get("recall_count", 0),
            formation_type=data.get("formation_type", "direct"),
            source_subject_id=data.get("source_subject_id"),
        )