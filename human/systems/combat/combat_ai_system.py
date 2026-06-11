#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:combat_ai_system.py
@说明:战斗 AI 系统
@时间:2026/05/29
@版本:1.0

根据情绪和性格自动触发战斗行为
'''

import random

from core.system import System
from core.world import World

from core.components.action_component import (
    ActionComponent, ActionType, ActionStatus
)
from human.components.combat.combat_stats_component import CombatStatsComponent
from human.components.cognitive.emotion_component import EmotionComponent
from human.components.cognitive.personality_component import PersonalityComponent
from core.components.vision_component import VisionComponent
from human.components.social.relationship_component import RelationshipComponent


class CombatAISystem(System):
    tick_interval = 3  # 每3帧执行一次（战斗AI决策不需要每帧）
    """
    战斗 AI 系统
    根据情绪状态和性格特征自动决策是否攻击或逃跑
    """

    ANGER_THRESHOLD = 0.7
    FEAR_THRESHOLD = 0.7
    AGGRESSION_THRESHOLD = 0.6

    def update(self, world: World, dt: float):
        for entity, (action, combat_stats, emotion, personality, vision) in world.get_components(
            ActionComponent, CombatStatsComponent, EmotionComponent,
            PersonalityComponent, VisionComponent
        ):
            action: ActionComponent
            combat_stats: CombatStatsComponent
            emotion: EmotionComponent
            personality: PersonalityComponent
            vision: VisionComponent

            # 只在 IDLE 状态下触发 AI 决策
            if action.current_action not in (ActionType.IDLE, ActionType.WAIT):
                continue

            # 1. 恐惧 -> 逃跑
            if emotion.fear >= self.FEAR_THRESHOLD:
                threat = self._find_nearest_threat(world, entity, vision)
                if threat is not None:
                    action.current_action = ActionType.FLEE
                    action.status = ActionStatus.RUNNING
                    action.target_entity = threat.id
                    emotion.adjust_emotion("fear", -0.1)  # 决策后稍微缓解
                    continue

            # 2. 愤怒 + 高侵略性 -> 攻击
            if (emotion.anger >= self.ANGER_THRESHOLD
                    and combat_stats.aggression >= self.AGGRESSION_THRESHOLD):
                target = self._find_attack_target(world, entity, vision)
                if target is not None:
                    action.current_action = ActionType.ATTACK
                    action.status = ActionStatus.RUNNING
                    action.target_entity = target.id
                    continue

            # 3. 性格冲动 + 非友好关系 -> 低概率攻击
            if (personality.bravery > 0.7
                    and random.random() < 0.01 * combat_stats.aggression * dt):
                target = self._find_attack_target(world, entity, vision)
                if target is not None:
                    action.current_action = ActionType.ATTACK
                    action.status = ActionStatus.RUNNING
                    action.target_entity = target.id

    def _find_nearest_threat(self, world, entity, vision):
        """在视野中寻找最近的威胁（简化：任意其他人类）"""
        best = None
        best_dist = float("inf")

        from space.space_component import SpaceComponent
        self_space = world.get_component(entity, SpaceComponent)
        if self_space is None:
            return None

        for eid in vision.entity_ids:
            candidate = world.query_entity(eid)
            if candidate is None or not candidate.is_alive():
                continue
            if candidate.id == entity.id:
                continue

            # 只把带 CombatStatsComponent 的视为威胁
            if world.get_component(candidate, CombatStatsComponent) is None:
                continue

            c_space = world.get_component(candidate, SpaceComponent)
            if c_space is None:
                continue

            dist = abs(c_space.x - self_space.x) + abs(c_space.y - self_space.y)
            if dist < best_dist:
                best_dist = dist
                best = candidate

        return best

    def _find_attack_target(self, world, entity, vision):
        """在视野中寻找攻击目标（优先关系差的）"""
        best = None
        best_score = -float("inf")

        from space.space_component import SpaceComponent
        self_space = world.get_component(entity, SpaceComponent)
        if self_space is None:
            return None

        relation = world.get_component(entity, RelationshipComponent)

        for eid in vision.entity_ids:
            candidate = world.query_entity(eid)
            if candidate is None or not candidate.is_alive():
                continue
            if candidate.id == entity.id:
                continue

            if world.get_component(candidate, CombatStatsComponent) is None:
                continue

            c_space = world.get_component(candidate, SpaceComponent)
            if c_space is None:
                continue

            dist = abs(c_space.x - self_space.x) + abs(c_space.y - self_space.y)

            # 评分：距离越近越好，关系越差越好
            score = -dist * 0.5
            if relation and candidate.id in relation.relations:
                score -= relation.relations[candidate.id] * 0.1

            if score > best_score:
                best_score = score
                best = candidate

        return best
