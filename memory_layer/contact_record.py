#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接触记录

主体与实体的客观交互记录，作为主观记忆形成的基础素材。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ContactRecord:
    """
    接触记录

    客观记录主体与实体的交互，不带有主观色彩。
    """
    contact_id: str
    subject_id: int
    subject_type: str                # "ANIMAL" / "HUMAN"
    entity_id: int
    concept_id: str                  # 关联的概念ID

    contact_type: str                # "visual", "physical", "auditory", "olfactory", "narrative"
    timestamp: float

    # 接触详情
    duration: float = 0.0            # 接触持续时间
    intensity: float = 0.5           # 强度 0.0~1.0
    context: Optional[str] = None    # 上下文: "在河边散步时"

    # 主体状态（记录时的状态，影响记忆形成）
    subject_emotional_state: Optional[str] = None  # "calm", "fearful", "excited"
    subject_attention_level: float = 0.5           # 注意力水平 0.0~1.0

    def to_dict(self) -> dict:
        return {
            "contact_id": self.contact_id,
            "subject_id": self.subject_id,
            "subject_type": self.subject_type,
            "entity_id": self.entity_id,
            "concept_id": self.concept_id,
            "contact_type": self.contact_type,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "intensity": self.intensity,
            "context": self.context,
            "subject_emotional_state": self.subject_emotional_state,
            "subject_attention_level": self.subject_attention_level,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContactRecord":
        return cls(
            contact_id=data["contact_id"],
            subject_id=data["subject_id"],
            subject_type=data["subject_type"],
            entity_id=data["entity_id"],
            concept_id=data["concept_id"],
            contact_type=data["contact_type"],
            timestamp=data["timestamp"],
            duration=data.get("duration", 0.0),
            intensity=data.get("intensity", 0.5),
            context=data.get("context"),
            subject_emotional_state=data.get("subject_emotional_state"),
            subject_attention_level=data.get("subject_attention_level", 0.5),
        )
