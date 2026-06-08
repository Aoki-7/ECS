#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物社交组件

存储动物的社交关系与群体信息。
"""

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component


@dataclass(slots=True)
class AnimalSocialComponent(Component):
    """
    动物社交组件

    属性:
        group_id: 所属群体 ID (-1 表示独行)
        group_role: 群体角色 ("leader", "member", "loner")
        mate_id: 配偶实体 ID (-1 表示无配偶)
        offspring_ids: 后代实体 ID 列表
        relationship_scores: 与其他实体的关系分数 {-1~1}
        pack_size_preference: 偏好的群体大小
    """
    group_id: int = -1
    group_role: str = "loner"
    mate_id: int = -1
    offspring_ids: List[int] = field(default_factory=list)
    relationship_scores: Dict[int, float] = field(default_factory=dict)
    pack_size_preference: int = 5

    def add_offspring(self, offspring_id: int) -> None:
        """添加后代"""
        if offspring_id not in self.offspring_ids:
            self.offspring_ids.append(offspring_id)

    def update_relationship(self, other_id: int, delta: float) -> None:
        """更新与某实体的关系分数"""
        current = self.relationship_scores.get(other_id, 0.0)
        self.relationship_scores[other_id] = max(-1.0, min(1.0, current + delta))

    def get_relationship(self, other_id: int) -> float:
        """获取与某实体的关系分数"""
        return self.relationship_scores.get(other_id, 0.0)
