#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
ConflictResolutionSystem - 冲突解决系统

职责：
- 管理冲突实例的生命周期
- 提供解决策略建议
- 跟踪冲突解决结果
- 评估关系影响

原 ConflictManagementSystem 的解决逻辑已迁移至此。
"""

import random
from typing import Dict, List, Optional, Tuple

from core.system import System
from core.world import World

from human.systems.interaction.conflict_models import (
    ConflictType,
    ResolutionStrategy,
    RelationshipQuality,
    ConflictInstance,
)


class ConflictResolutionSystem(System):
    tick_interval = 5  # 每5帧执行一次
    _MAX_HISTORY_SIZE = 100
    _MAX_RESOLVED_SIZE = 100
    """
    冲突解决系统

    管理冲突实例的创建、策略推荐和解决。
    """

    priority = 32  # 在 ConflictDetectionSystem(31) 之后

    def __init__(self):
        super().__init__()
        self.active_conflicts: List[ConflictInstance] = []
        self.resolved_conflicts: List[ConflictInstance] = []
        self.resolution_history: List[Dict] = []
        self.relationship_quality: Dict[int, RelationshipQuality] = {}

    def _add_resolution_history(self, entry: dict) -> None:
        self.resolution_history.append(entry)
        if len(self.resolution_history) > self._MAX_HISTORY_SIZE:
            self.resolution_history.pop(0)

    def add_conflict(self, conflict_type, description: str, entities: List[int]) -> ConflictInstance:
        """添加/记录一个冲突事件"""
        conflict = ConflictInstance(
            conflict_type=conflict_type,
            description=description,
            parties=[e for e in entities if e],
            intensity=self._calculate_intensity(entities, description)
        )
        self.active_conflicts.append(conflict)
        return conflict

    def _calculate_intensity(self, entities: List[int], desc: str) -> float:
        """计算冲突强度"""
        intensity = len(entities) * 25
        keywords = ["严重", "激烈", "致命", "暴力", "永久"]
        if any(kw in desc for kw in keywords):
            intensity += 30
        return min(100, intensity)

    def propose_resolution(self, conflict: ConflictInstance) -> List[Tuple[ResolutionStrategy, str]]:
        """为冲突推荐解决策略"""
        suggestions = []
        ctype = getattr(conflict, 'conflict_type', None)

        if ctype == "RESOURCE":
            suggestions.append((ResolutionStrategy.COMPROMISE, "双方各退一步，共享资源"))
            suggestions.append((ResolutionStrategy.COLLABORATION, "合作开发新方案，扩大资源"))
        elif ctype == "VALUES":
            suggestions.append((ResolutionStrategy.ACCOMMODATION, "尊重差异，各自坚持"))
            suggestions.append((ResolutionStrategy.DIALOGUE, "深入沟通，寻找共同基础"))
        elif ctype == "RELATIONAL":
            suggestions.append((ResolutionStrategy.COLLABORATION, "重建信任，修复关系"))
            suggestions.append((ResolutionStrategy.ACCOMMODATION, "一方做出让步，缓和关系"))
        else:
            suggestions.append((ResolutionStrategy.DIALOGUE, "坦诚沟通，解决问题"))

        return suggestions

    def resolve_conflict(self, conflict: ConflictInstance, resolution_method: ResolutionStrategy) -> Dict:
        """解决冲突"""
        conflict.current_phase = "resolution"
        conflict.resolution_method = resolution_method.name if resolution_method else None

        result = {
            "conflict_id": conflict.id,
            "method_used": resolution_method.name if resolution_method else None,
            "outcome": self._simulate_outcome(resolution_method),
            "parties_involved": conflict.parties.copy(),
        }

        for party in conflict.parties:
            if party not in self.relationship_quality:
                self.relationship_quality[party] = RelationshipQuality.STABLE

        conflict.current_phase = "resolved"
        conflict.outcome = result["outcome"]
        self.resolved_conflicts.append(conflict)
        if len(self.resolved_conflicts) > self._MAX_RESOLVED_SIZE:
            self.resolved_conflicts.pop(0)
        self._add_resolution_history(result)

        return result

    def _simulate_outcome(self, method: ResolutionStrategy) -> str:
        """模拟冲突解决结果"""
        outcomes = {
            ResolutionStrategy.AVOIDANCE: "暂时搁置问题，避免正面冲突。关系维持现状。",
            ResolutionStrategy.COMPROMISE: "双方各让一步，达成妥协方案。关系略有改善。",
            ResolutionStrategy.COMPETITION: "一方取得优势，但可能造成关系紧张。",
            ResolutionStrategy.COLLABORATION: "共同努力寻找双赢方案。关系显著改善。",
            ResolutionStrategy.ACCOMMODATION: "一方让步，另一方满意。依赖程度增加。",
            ResolutionStrategy.DIALOGUE: "通过沟通达成共识。",
        }
        return outcomes.get(method, "问题解决。")

    def update(self, world: World, dt: float = 0.0):
        """每 tick 自动尝试解决低强度冲突"""
        super().update(world, dt)

        for conflict in list(self.active_conflicts):
            if conflict.current_phase == "resolved":
                continue

            # 低强度冲突自动衰减
            if conflict.intensity < 20:
                conflict.intensity -= 2.0 * dt
                if conflict.intensity <= 0:
                    self.resolve_conflict(conflict, ResolutionStrategy.AVOIDANCE)
