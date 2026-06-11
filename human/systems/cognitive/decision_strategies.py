#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
决策策略模块

将 DecisionSystem 的评分逻辑拆分为独立的策略类，
便于单元测试和策略扩展。
'''

from abc import ABC, abstractmethod
from typing import Dict

from human.components.cognitive.intent_component import IntentType


class DecisionStrategy(ABC):
    """决策策略基类"""

    @abstractmethod
    def evaluate(self, scores: Dict[IntentType, float], context: dict) -> None:
        """
        评估意图得分

        Args:
            scores: 意图得分字典（修改此字典添加得分）
            context: 决策上下文，包含所有相关组件
        """
        pass


class PhysiologyStrategy(DecisionStrategy):
    """生理需求策略"""

    def evaluate(self, scores: Dict[IntentType, float], context: dict) -> None:
        needs = context['needs']
        health = context['health']

        # 口渴 → 找水
        if needs.thirst > 50:
            scores[IntentType.DRINK] = needs.thirst * 1.2
        # 饥饿 → 找食物
        if needs.hunger > 50:
            scores[IntentType.EAT] = needs.hunger * 1.1
        # 疲劳 → 休息
        if needs.energy < 30:
            scores[IntentType.REST] = (30 - needs.energy) * 1.5
        # 低生命值 → 治疗/逃跑
        if health and health.hp < health.max_hp * 0.3:
            scores[IntentType.FLEE] = (1.0 - health.hp / health.max_hp) * 100


class EmotionStrategy(DecisionStrategy):
    """情绪影响策略"""

    def evaluate(self, scores: Dict[IntentType, float], context: dict) -> None:
        emotion = context['emotion']
        intent = context['intent']
        is_critical = context['is_survival_critical']

        if is_critical:
            return  # 紧急状态下情绪不主导

        # 快乐 → 社交/探索
        if emotion.happiness > 0.6:
            scores[IntentType.SOCIALIZE] = emotion.happiness * 50
            scores[IntentType.EXPLORE] = emotion.happiness * 30
        # 悲伤 → 休息/独处
        if emotion.sadness > 0.5:
            scores[IntentType.REST] = emotion.sadness * 40
        # 愤怒 → 攻击
        if emotion.anger > 0.6:
            scores[IntentType.ATTACK] = emotion.anger * 60
        # 恐惧 → 逃跑
        if emotion.fear > 0.5:
            scores[IntentType.FLEE] = emotion.fear * 70


class PersonalityStrategy(DecisionStrategy):
    """性格影响策略"""

    def evaluate(self, scores: Dict[IntentType, float], context: dict) -> None:
        personality = context['personality']
        is_critical = context['is_survival_critical']

        if is_critical or not personality:
            return

        # 外向 → 社交
        if personality.extraversion > 0.6:
            scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) + personality.extraversion * 20
        # 神经质 → 更容易恐惧/焦虑
        if personality.neuroticism > 0.6:
            scores[IntentType.FLEE] = scores.get(IntentType.FLEE, 0) + personality.neuroticism * 15
        # 开放性 → 探索
        if personality.openness > 0.6:
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + personality.openness * 25
        # 尽责性 → 工作/目标导向
        if personality.conscientiousness > 0.6:
            scores[IntentType.WORK] = scores.get(IntentType.WORK, 0) + personality.conscientiousness * 20


class MemoryStrategy(DecisionStrategy):
    """记忆影响策略"""

    def evaluate(self, scores: Dict[IntentType, float], context: dict) -> None:
        memory = context['memory']
        needs = context['needs']
        is_critical = context['is_survival_critical']

        if is_critical or not memory:
            return

        # 如果记得水源位置，增加找水意图
        if needs.thirst > 30 and memory.has_memory_of('water_source'):
            scores[IntentType.DRINK] = scores.get(IntentType.DRINK, 0) + 15
        # 如果记得食物位置，增加觅食意图
        if needs.hunger > 30 and memory.has_memory_of('food_source'):
            scores[IntentType.EAT] = scores.get(IntentType.EAT, 0) + 15


class GoalStrategy(DecisionStrategy):
    """目标影响策略"""

    def evaluate(self, scores: Dict[IntentType, float], context: dict) -> None:
        goal = context['goal']
        is_critical = context['is_survival_critical']

        if is_critical or not goal:
            return

        # 根据当前目标增加对应意图得分
        if goal.current_goal == 'build_shelter':
            scores[IntentType.WORK] = scores.get(IntentType.WORK, 0) + 30
        elif goal.current_goal == 'find_mate':
            scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) + 25
        elif goal.current_goal == 'explore':
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + 35


class SocialStrategy(DecisionStrategy):
    """社交影响策略"""

    def evaluate(self, scores: Dict[IntentType, float], context: dict) -> None:
        relation = context['relation']
        is_critical = context['is_survival_critical']

        if is_critical or not relation:
            return

        # 有伴侣时增加社交意图
        if relation.partner_id is not None:
            scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) + 10
        # 有敌人时增加攻击或逃跑
        if relation.enemies:
            scores[IntentType.ATTACK] = scores.get(IntentType.ATTACK, 0) + 20
            scores[IntentType.FLEE] = scores.get(IntentType.FLEE, 0) + 15


class CircadianStrategy(DecisionStrategy):
    """昼夜节律策略"""

    def evaluate(self, scores: Dict[IntentType, float], context: dict) -> None:
        circadian = context['circadian']
        is_critical = context['is_survival_critical']

        if is_critical or not circadian:
            return

        # 夜间降低活动意图，增加休息 (phase 接近 0.0 或 1.0 为夜间)
        is_night = circadian.phase < 0.25 or circadian.phase > 0.75
        is_day = 0.25 <= circadian.phase <= 0.75
        
        if is_night:
            scores[IntentType.REST] = scores.get(IntentType.REST, 0) + 20
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) - 15
            scores[IntentType.WORK] = scores.get(IntentType.WORK, 0) - 10
        # 白天增加活动
        elif is_day:
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + 10
            scores[IntentType.WORK] = scores.get(IntentType.WORK, 0) + 10


class EmergencyStrategy(DecisionStrategy):
    """紧急状态策略"""

    def evaluate(self, scores: Dict[IntentType, float], context: dict) -> None:
        is_critical = context['is_survival_critical']
        needs = context['needs']
        health = context['health']

        if not is_critical:
            return

        # 紧急状态下大幅提升生存意图
        if needs.thirst > 80:
            scores[IntentType.DRINK] = 200  # 最高优先级
        if needs.hunger > 80:
            scores[IntentType.EAT] = 190
        if needs.energy < 10:
            scores[IntentType.REST] = 180
        if health and health.hp < health.max_hp * 0.1:
            scores[IntentType.FLEE] = 250  # 濒死时优先逃跑
