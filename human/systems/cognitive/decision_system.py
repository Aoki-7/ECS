#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:decision_system.py
@说明:决策系统 v2.0
@时间:2026/05/25
@作者:AI Assistant
@版本:2.0

增强版决策系统：
- 与 IntentSystem 协同工作，在生理需求意图基础上叠加情绪/性格/记忆/目标影响
- 情绪状态可以覆盖或调整意图优先级
- 性格特征影响长期行为偏好
- 记忆提供经验指导（上次在哪里找到水？）
- 目标引导非紧急状态下的行为方向
- 生成内心思维记录到 BrainComponent
'''

import random

from core.system import System
from core.world import World

from human.components.cognitive.intent_component import IntentComponent, IntentType
from human.components.cognitive.emotion_component import EmotionComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.cognitive.personality_component import PersonalityComponent
from human.components.cognitive.brain_component import BrainComponent
from human.components.cognitive.goal_component import GoalComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.health_status_component import HealthStatusComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from human.components.social.relationship_component import RelationshipComponent, RelationshipStatus


class DecisionSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    决策系统 v2.0
    
    核心设计理念：多层决策模型
    Layer 1 (IntentSystem): 生理需求驱动（已处理）
    Layer 2 (DecisionSystem): 心理/认知/社交层叠加
    
    当生理需求不紧急时，情绪、性格、记忆和目标主导行为选择。
    当生理需求紧急时，这些因子只调整优先级而非覆盖。
    """

    # 生理紧急阈值
    CRITICAL_THIRST = 80
    CRITICAL_HUNGER = 80
    CRITICAL_ENERGY = 20

    def update(self, world: World, dt: float):
        current_time = world.get_time().total_hours

        for entity, (intent, emotion, memory, personality, brain, health, needs) in world.get_components(
            IntentComponent, EmotionComponent, MemoryComponent, 
            PersonalityComponent, BrainComponent, HealthStatusComponent,
            PhysiologyNeedsComponent
        ):
            self._make_decision(
                world, entity, 
                intent, emotion, memory, personality, brain, health, needs,
                current_time, dt
            )

    def _make_decision(self, world: World, entity, 
                      intent: IntentComponent, emotion: EmotionComponent, 
                      memory: MemoryComponent, personality: PersonalityComponent,
                      brain: BrainComponent, health: HealthStatusComponent,
                      needs: PhysiologyNeedsComponent,
                      current_time: float, dt: float):
        """为单个实体做出决策"""
        
        # 获取当前生理紧急程度
        is_survival_critical = (
            needs.thirst > self.CRITICAL_THIRST or
            needs.hunger > self.CRITICAL_HUNGER or
            needs.energy < self.CRITICAL_ENERGY or
            (health and health.hp < health.max_hp * 0.2)
        )
        
        # 获取目标组件
        goal = world.get_component(entity, GoalComponent)
        relation = world.get_component(entity, RelationshipComponent)
        age = world.get_component(entity, LifeCycleComponent)
        
        # 计算各意图的加权得分
        scores = self._evaluate_all_factors(
            world, entity, intent, emotion, memory, personality, 
            goal, relation, age, needs, health, is_survival_critical
        )
        
        # 生理紧急时，禁止覆盖生存意图
        if is_survival_critical:
            # 只允许情绪微调现有意图的紧迫度
            self._apply_emergency_modifiers(intent, emotion, scores)
        else:
            # 非紧急状态：情绪/性格/记忆/目标可以自由引导行为
            # 选择得分最高的意图（排除被锁定的）
            if scores and not intent.locked:
                best_intent, best_score = max(scores.items(), key=lambda x: x[1])
                # 只有当新意图显著优于当前意图时才切换
                current_score = scores.get(intent.intent, 0)
                if best_score > current_score + 5.0:
                    intent.intent = best_intent
                    intent.priority = best_score
                    brain.set_thought(f"我决定{best_intent.name}")
        
        # 无论是否切换，都更新决策信心和心理状态
        brain.decision_confidence = min(1.0, scores.get(intent.intent, 50) / 100.0)
        brain.update_mental_state(emotion.get_mood_score(), emotion.stress)
        
        # 记录决策到记忆
        if memory and not is_survival_critical:
            memory.add_event(
                current_time, "decision",
                f"决定执行{intent.intent.name}",
                impact=emotion.get_mood_score() * 0.3
            )

    def _evaluate_all_factors(self, world, entity, intent, emotion, memory, 
                               personality, goal, relation, age, needs, health,
                               is_survival_critical) -> dict:
        """综合评估所有因素，返回各意图得分"""
        scores = {}
        
        # 基础生理得分（从 IntentSystem 继承的逻辑）
        self._score_physiology(scores, needs, health)
        
        # 情绪层影响
        self._score_emotions(scores, emotion, is_survival_critical)
        
        # 性格层影响
        self._score_personality(scores, personality, is_survival_critical)
        
        # 记忆层影响
        self._score_memory(scores, memory, needs, is_survival_critical)
        
        # 目标层影响
        self._score_goals(scores, goal, relation, age, is_survival_critical)
        
        # 社交状态影响
        self._score_social(scores, relation, emotion, is_survival_critical)
        
        return scores

    def _score_physiology(self, scores: dict, needs, health):
        """生理需求基础得分"""
        if needs.thirst > 70:
            scores[IntentType.DRINK] = scores.get(IntentType.DRINK, 0) + 100
        elif needs.thirst > 50:
            scores[IntentType.DRINK] = scores.get(IntentType.DRINK, 0) + 60
        elif needs.thirst > 30:
            scores[IntentType.DRINK] = scores.get(IntentType.DRINK, 0) + 20
        
        if needs.hunger > 70:
            scores[IntentType.EAT] = scores.get(IntentType.EAT, 0) + 95
        elif needs.hunger > 50:
            scores[IntentType.EAT] = scores.get(IntentType.EAT, 0) + 55
        elif needs.hunger > 30:
            scores[IntentType.EAT] = scores.get(IntentType.EAT, 0) + 15
        
        if needs.energy < 20:
            scores[IntentType.SLEEP] = scores.get(IntentType.SLEEP, 0) + 85
        elif needs.energy < 40:
            scores[IntentType.REST] = scores.get(IntentType.REST, 0) + 40
        
        if health and health.hp < health.max_hp * 0.3:
            scores[IntentType.HEAL] = scores.get(IntentType.HEAL, 0) + 70
        elif health and health.hp < health.max_hp * 0.6:
            scores[IntentType.HEAL] = scores.get(IntentType.HEAL, 0) + 30

    def _score_emotions(self, scores: dict, emotion: EmotionComponent, is_survival_critical: bool):
        """情绪对意图的影响"""
        if not emotion:
            return
        
        # 恐惧 → 逃跑/躲藏优先级提升
        if emotion.fear > 0.5:
            scores[IntentType.FLEE] = scores.get(IntentType.FLEE, 0) + emotion.fear * 80
            scores[IntentType.HIDE] = scores.get(IntentType.HIDE, 0) + emotion.fear * 40
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) - 30
        
        # 愤怒 → 攻击倾向（如果非生存紧急）
        if emotion.anger > 0.6 and not is_survival_critical:
            scores[IntentType.ATTACK] = scores.get(IntentType.ATTACK, 0) + emotion.anger * 40
            scores[IntentType.FLEE] = scores.get(IntentType.FLEE, 0) - 20
        
        # 悲伤 → 降低积极行为，倾向休息
        if emotion.sadness > 0.5:
            scores[IntentType.REST] = scores.get(IntentType.REST, 0) + emotion.sadness * 30
            scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) - 15
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) - 20
        
        # 快乐/喜悦 → 倾向社交和探索
        if emotion.joy > 0.4 or emotion.happiness > 0.6:
            scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) + 25
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + 20
        
        # 孤独 → 强烈倾向社交
        if emotion.loneliness > 0.5:
            scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) + emotion.loneliness * 50
            scores[IntentType.PAIR] = scores.get(IntentType.PAIR, 0) + emotion.loneliness * 30
        
        # 兴奋 → 倾向探索和收集
        if emotion.excitement > 0.4:
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + emotion.excitement * 35
            scores[IntentType.COLLECT] = scores.get(IntentType.COLLECT, 0) + emotion.excitement * 20
        
        # 压力 → 倾向安全行为
        if emotion.stress > 0.6:
            scores[IntentType.REST] = scores.get(IntentType.REST, 0) + emotion.stress * 25
            scores[IntentType.HIDE] = scores.get(IntentType.HIDE, 0) + emotion.stress * 15
        
        # 高平静度 → 倾向工作和建造
        if emotion.calmness > 0.6 and not is_survival_critical:
            scores[IntentType.WORK] = scores.get(IntentType.WORK, 0) + emotion.calmness * 20
            scores[IntentType.BUILD] = scores.get(IntentType.BUILD, 0) + emotion.calmness * 15

    def _score_personality(self, scores: dict, personality: PersonalityComponent, is_survival_critical: bool):
        """性格对意图的影响"""
        if not personality or is_survival_critical:
            return
        
        # 勇敢 → 降低逃跑，增加探索和攻击
        if personality.bravery > 0.6:
            scores[IntentType.FLEE] = scores.get(IntentType.FLEE, 0) - personality.bravery * 30
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + personality.bravery * 20
            scores[IntentType.ATTACK] = scores.get(IntentType.ATTACK, 0) + personality.bravery * 15
        elif personality.bravery < 0.3:
            scores[IntentType.FLEE] = scores.get(IntentType.FLEE, 0) + 15
            scores[IntentType.HIDE] = scores.get(IntentType.HIDE, 0) + 10
        
        # 贪婪 → 增加收集和存储
        if personality.greed > 0.6:
            scores[IntentType.COLLECT] = scores.get(IntentType.COLLECT, 0) + personality.greed * 25
            scores[IntentType.STORE] = scores.get(IntentType.STORE, 0) + personality.greed * 20
        
        # 善良 → 增加社交和帮助
        if personality.kindness > 0.6:
            scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) + personality.kindness * 20
            scores[IntentType.HEAL] = scores.get(IntentType.HEAL, 0) + personality.kindness * 15
        
        # 好奇心 → 增加探索和调查
        if personality.curiosity > 0.6:
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + personality.curiosity * 25
            scores[IntentType.INVESTIGATE] = scores.get(IntentType.INVESTIGATE, 0) + personality.curiosity * 20
        elif personality.curiosity < 0.3:
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) - 10
        
        # 守序/纪律 → 增加工作和建造
        if personality.discipline > 0.6:
            scores[IntentType.WORK] = scores.get(IntentType.WORK, 0) + personality.discipline * 25
            scores[IntentType.BUILD] = scores.get(IntentType.BUILD, 0) + personality.discipline * 20
            scores[IntentType.REST] = scores.get(IntentType.REST, 0) + personality.discipline * 10

    def _score_memory(self, scores: dict, memory: MemoryComponent, needs, is_survival_critical: bool):
        """记忆对意图的影响"""
        if not memory:
            return
        
        # 最近找到水的记忆 → 增加探索信心
        recent_water = memory.get_recent_events(3, "found_water")
        if recent_water:
            avg_impact = sum(e["impact"] for e in recent_water) / len(recent_water)
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + avg_impact * 15
        
        # 最近社交成功的记忆 → 增加社交倾向
        if memory.recent_successes.get("socialize", 0) > 2:
            scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) + 20
        
        # 最近探索成功的记忆 → 增加探索
        if memory.recent_successes.get("explore", 0) > 2:
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + 15
        
        # 负面事件记忆 → 增加警惕
        recent_negative = [e for e in memory.events[-10:] if e.get("impact", 0) < -0.5]
        if len(recent_negative) >= 3:
            scores[IntentType.HIDE] = scores.get(IntentType.HIDE, 0) + 15
            scores[IntentType.FLEE] = scores.get(IntentType.FLEE, 0) + 10

    def _score_goals(self, scores: dict, goal, relation, age, is_survival_critical: bool):
        """目标对意图的影响"""
        if not goal or not goal.current_goal or is_survival_critical:
            return
        
        current = goal.current_goal
        
        # 目标关键词映射到意图
        if "伴侣" in current or "配偶" in current or "家庭" in current:
            if relation and relation.status == RelationshipStatus.SINGLE:
                scores[IntentType.PAIR] = scores.get(IntentType.PAIR, 0) + 30
                scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) + 15
        
        elif "资源" in current or "财富" in current or "资金" in current:
            scores[IntentType.COLLECT] = scores.get(IntentType.COLLECT, 0) + 25
            scores[IntentType.WORK] = scores.get(IntentType.WORK, 0) + 20
        
        elif "探索" in current or "发现" in current:
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + 25
            scores[IntentType.INVESTIGATE] = scores.get(IntentType.INVESTIGATE, 0) + 15
        
        elif "建造" in current or "改进" in current:
            scores[IntentType.BUILD] = scores.get(IntentType.BUILD, 0) + 25
            scores[IntentType.CRAFT] = scores.get(IntentType.CRAFT, 0) + 15
        
        elif "朋友" in current or "社交" in current:
            scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) + 25
        
        elif "学习" in current or "知识" in current:
            scores[IntentType.EXPLORE] = scores.get(IntentType.EXPLORE, 0) + 15
            scores[IntentType.WORK] = scores.get(IntentType.WORK, 0) + 10

    def _score_social(self, scores: dict, relation, emotion, is_survival_critical: bool):
        """社交状态对意图的影响"""
        if not relation or is_survival_critical:
            return
        
        # 单身且社交需求 → 配对
        if relation.status == RelationshipStatus.SINGLE:
            if emotion and emotion.loneliness > 0.3:
                scores[IntentType.PAIR] = scores.get(IntentType.PAIR, 0) + emotion.loneliness * 25
        
        # 已婚 → 社交和工作平衡
        elif relation.status == RelationshipStatus.MARRIED:
            scores[IntentType.SOCIALIZE] = scores.get(IntentType.SOCIALIZE, 0) + 10
            scores[IntentType.WORK] = scores.get(IntentType.WORK, 0) + 10

    def _apply_emergency_modifiers(self, intent: IntentComponent, emotion: EmotionComponent, scores: dict):
        """生理紧急状态下的情绪微调（不覆盖生存意图）"""
        if not emotion:
            return
        
        # 极度恐惧时，即使口渴也可能先逃跑
        if emotion.fear > 0.8 and scores.get(IntentType.FLEE, 0) > scores.get(intent.intent, 0):
            intent.intent = IntentType.FLEE
            intent.priority = emotion.fear * 100