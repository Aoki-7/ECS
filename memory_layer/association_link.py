#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联想链接

主体记忆中的概念关联网络。
"""

from dataclasses import dataclass


@dataclass
class AssociationLink:
    """
    联想链接

    连接两个概念的关系，带有强度权重。
    """
    target_concept_id: str             # 关联的目标概念ID
    relation_type: str                 # 关系类型
    strength: float = 0.5              # 联想强度 0.0~1.0

    # 预定义关系类型
    SIMILAR_TO = "similar_to"          # 相似
    OPPOSITE_OF = "opposite_of"        # 相反
    PART_OF = "part_of"                # 组成部分
    CAUSED_BY = "caused_by"            # 因果关系
    LOCATED_NEAR = "located_near"      # 空间邻近
    TEMPORAL_SEQUENCE = "temporal_sequence"  # 时间先后

    def to_dict(self) -> dict:
        return {
            "target_concept_id": self.target_concept_id,
            "relation_type": self.relation_type,
            "strength": self.strength,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AssociationLink":
        return cls(
            target_concept_id=data["target_concept_id"],
            relation_type=data["relation_type"],
            strength=data.get("strength", 0.5),
        )
