#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客观记忆：Concept

被记忆的对象本身，独立于任何主体存在。
实体消亡后，Concept 仍然保留作为客观事实。
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Set
from enum import Enum, auto

from .sensory_description import SensoryDescription


class ConceptType(Enum):
    """概念类型"""
    ENTITY = auto()      # 来源于实体
    ABSTRACT = auto()    # 抽象概念（如"爱情"）
    MYTH = auto()        # 神话/虚构（如"龙"）
    EVENT = auto()       # 事件（如"那场洪水"）


@dataclass
class Concept:
    """
    客观记忆 = 被记忆的对象本身

    类似数据库"事实表"中的一条记录。
    即使所有主体都消亡，客观事实仍然存在。
    """
    concept_id: str                    # 唯一标识 (如 "entity_42_stone")
    name: str                          # 名称
    concept_type: ConceptType          # 概念类型

    # === 客观描述（结构化）===
    canonical_description: SensoryDescription  # 客观感官属性
    physical_properties: Dict[str, any] = field(default_factory=dict)  # 物理属性

    # === 来源追踪 ===
    source_entity_id: Optional[int] = None     # 来源实体（可能已消亡）
    source_entity_type: Optional[str] = None   # 实体类型
    created_at: float = 0.0                    # 概念形成时间
    destroyed_at: Optional[float] = None       # 实体消亡时间（如适用）

    # === 状态 ===
    is_active: bool = True                     # 是否还有对应实体存在

    # === 关联 ===
    related_concepts: Set[str] = field(default_factory=set)  # 关联概念ID

    def mark_destroyed(self, timestamp: float) -> None:
        """标记来源实体已消亡"""
        self.is_active = False
        self.destroyed_at = timestamp

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "concept_id": self.concept_id,
            "name": self.name,
            "concept_type": self.concept_type.name,
            "canonical_description": self.canonical_description.to_dict(),
            "physical_properties": self.physical_properties,
            "source_entity_id": self.source_entity_id,
            "source_entity_type": self.source_entity_type,
            "created_at": self.created_at,
            "destroyed_at": self.destroyed_at,
            "is_active": self.is_active,
            "related_concepts": list(self.related_concepts),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Concept":
        """从字典反序列化"""
        return cls(
            concept_id=data["concept_id"],
            name=data["name"],
            concept_type=ConceptType[data["concept_type"]],
            canonical_description=SensoryDescription.from_dict(data["canonical_description"]),
            physical_properties=data.get("physical_properties", {}),
            source_entity_id=data.get("source_entity_id"),
            source_entity_type=data.get("source_entity_type"),
            created_at=data.get("created_at", 0.0),
            destroyed_at=data.get("destroyed_at"),
            is_active=data.get("is_active", True),
            related_concepts=set(data.get("related_concepts", [])),
        )