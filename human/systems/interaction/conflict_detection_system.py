#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
ConflictDetectionSystem - 冲突检测系统

职责：
- 扫描 RelationshipComponent，检测负面关系
- 自动创建 ConflictComponent 中的冲突记录
- 冲突强度高时设置 ActionType.ATTACK

原 ConflictManagementSystem 的检测逻辑已迁移至此。
"""

import random
import logging
from typing import Optional

from core.system import System
from core.world import World

from human.components.social.conflict_component import ConflictComponent
from human.components.social.relationship_component import RelationshipComponent
from human.components.cognitive.personality_component import PersonalityComponent
from human.components.cognitive.emotion_component import EmotionComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.systems.interaction.conflict_resolution_system import ResolutionStrategy

logger = logging.getLogger(__name__)


class ConflictType:
    RELATIONAL = "RELATIONAL"


class ConflictDetectionSystem(System):
    tick_interval = 5  # 每5帧执行一次
    """
    冲突检测系统

    检测实体间的负面关系并创建冲突记录。
    """

    priority = 31  # 与原 ConflictManagementSystem 相同

    NEGATIVE_THRESHOLD = -20  # 关系分数低于此值触发冲突

    def update(self, world: World, dt: float = 0.0):
        super().update(world, dt)

        for entity, (relation, personality, emotion, action, conflict_comp) in world.get_components(
            RelationshipComponent, PersonalityComponent, EmotionComponent,
            ActionComponent, ConflictComponent
        ):
            relation: RelationshipComponent
            personality: PersonalityComponent
            emotion: EmotionComponent
            action: ActionComponent
            conflict_comp: ConflictComponent

            # 清理已解决的冲突
            for c in list(conflict_comp.active_conflicts):
                if c.get("intensity", 0) <= 0:
                    conflict_comp.remove_conflict(c["conflict_id"])

            # 检测负面关系
            if not hasattr(relation, 'relations') or not relation.relations:
                continue

            for other_id, score in list(relation.relations.items()):
                if score >= self.NEGATIVE_THRESHOLD:
                    continue

                # 检查是否已有活跃冲突
                existing = any(
                    c.get("opponent_id") == other_id
                    for c in conflict_comp.active_conflicts
                )
                if existing:
                    continue

                # 创建新冲突
                intensity = min(100, abs(score) * 0.5 + random.uniform(0, 10))
                strategy = self._choose_strategy(personality, emotion)

                conflict = {
                    "conflict_id": f"conflict_{entity.id}_{other_id}",
                    "type": ConflictType.RELATIONAL,
                    "opponent_id": other_id,
                    "intensity": intensity,
                    "strategy": strategy.name if strategy else "AVOIDANCE",
                }
                conflict_comp.add_conflict(conflict)

                # 冲突强度高时触发攻击
                if intensity > 60 and action.current_action in (ActionType.IDLE, ActionType.WAIT):
                    action.current_action = ActionType.ATTACK
                    action.status = ActionStatus.RUNNING
                    action.target_entity = other_id

                logger.debug(
                    f"[ConflictDetection] E{entity.id} vs E{other_id}: "
                    f"intensity={intensity:.1f}, strategy={strategy}"
                )

    @staticmethod
    def _choose_strategy(personality: PersonalityComponent, emotion: EmotionComponent) -> Optional[ResolutionStrategy]:
        """根据性格和情绪选择解决策略"""
        if personality.kindness > 0.7:
            return ResolutionStrategy.COLLABORATION
        if personality.greed > 0.7:
            return ResolutionStrategy.COMPETITION
        if emotion.fear > 0.6:
            return ResolutionStrategy.AVOIDANCE
        if emotion.anger > 0.6:
            return ResolutionStrategy.COMPETITION
        return ResolutionStrategy.COMPROMISE