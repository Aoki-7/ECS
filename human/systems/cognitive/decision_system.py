from human.systems.cognitive.memory_management_system import MemoryManagementSystem
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:decision_system.py
@说明:决策系统 v3.7 — 策略模式重构
@时间:2026/06/11
@作者:AI Assistant
@版本:3.7

v3.7 变更：
- 将评分逻辑拆分为独立策略类
- DecisionSystem 仅负责协调策略执行
- 便于单元测试和策略扩展
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
from biology.components.circadian_component import CircadianComponent
from biology.systems.circadian_system import CircadianSystem

from human.systems.cognitive.decision_strategies import (
    PhysiologyStrategy,
    EmotionStrategy,
    PersonalityStrategy,
    MemoryStrategy,
    GoalStrategy,
    SocialStrategy,
    CircadianStrategy,
    EmergencyStrategy,
)


class DecisionSystem(System):
    tick_interval = 5  # 每5帧执行一次（决策不需要每帧更新）
    """
    决策系统 v3.7
    
    核心设计理念：多层决策模型 + 策略模式
    Layer 1 (IntentSystem): 生理需求驱动（已处理）
    Layer 2 (DecisionSystem): 心理/认知/社交层叠加
    
    策略列表：
    - PhysiologyStrategy: 生理需求基础得分
    - EmotionStrategy: 情绪影响
    - PersonalityStrategy: 性格影响
    - MemoryStrategy: 记忆影响
    - GoalStrategy: 目标影响
    - SocialStrategy: 社交影响
    - CircadianStrategy: 昼夜节律修正
    - EmergencyStrategy: 紧急状态处理
    """

    # 生理紧急阈值
    CRITICAL_THIRST = 80
    CRITICAL_HUNGER = 80
    CRITICAL_ENERGY = 20

    def __init__(self):
        super().__init__()
        self._strategies = [
            PhysiologyStrategy(),
            EmotionStrategy(),
            PersonalityStrategy(),
            MemoryStrategy(),
            GoalStrategy(),
            SocialStrategy(),
            CircadianStrategy(),
            EmergencyStrategy(),
        ]

    def update(self, world: World, dt: float):
        time = world.get_time()
        # 防御：如果 get_time() 返回 None，使用默认值 0.0
        if time is None:
            current_time = 0.0
        else:
            current_time = time.total_hours

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
        
        # 获取额外组件
        goal = world.get_component(entity, GoalComponent)
        relation = world.get_component(entity, RelationshipComponent)
        age = world.get_component(entity, LifeCycleComponent)
        circadian = world.get_component(entity, CircadianComponent)
        
        # 构建上下文
        context = {
            'world': world,
            'entity': entity,
            'intent': intent,
            'emotion': emotion,
            'memory': memory,
            'personality': personality,
            'brain': brain,
            'health': health,
            'needs': needs,
            'goal': goal,
            'relation': relation,
            'age': age,
            'circadian': circadian,
            'is_survival_critical': is_survival_critical,
            'current_time': current_time,
            'dt': dt,
        }
        
        # 计算各意图的加权得分
        scores = {}
        for strategy in self._strategies:
            strategy.evaluate(scores, context)
        
        # 生理紧急时，禁止覆盖生存意图
        if is_survival_critical:
            # 只允许情绪微调现有意图的紧迫度
            self._apply_emergency_modifiers(intent, emotion, scores)
        else:
            # 非紧急状态：选择得分最高的意图
            if scores and not intent.locked:
                best_intent, best_score = max(scores.items(), key=lambda x: x[1])
                current_score = scores.get(intent.intent, 0)
                if best_score > current_score + 5.0:
                    intent.intent = best_intent
                    intent.priority = best_score
                    if hasattr(brain, 'set_thought'):
                        brain.set_thought(f"我决定{best_intent.name}")
                    else:
                        brain.thought = f"我决定{best_intent.name}"
        
        # 更新决策信心和心理状态
        if hasattr(brain, 'decision_confidence'):
            brain.decision_confidence = min(1.0, scores.get(intent.intent, 50) / 100.0)
        if hasattr(brain, 'update_mental_state'):
            mood_score = emotion.get_mood_score() if hasattr(emotion, 'get_mood_score') else 0.0
            brain.update_mental_state(mood_score, emotion.stress)
        else:
            brain.mental_state = emotion.get_mood_score() if hasattr(emotion, 'get_mood_score') else 0.0
        
        # 记录决策到记忆
        if memory and hasattr(memory, 'add_event') and not is_survival_critical:
            MemoryManagementSystem.add_event(memory, 
                current_time, "decision",
                f"决定执行{intent.intent.name}",
                impact=emotion.get_mood_score() * 0.3 if hasattr(emotion, 'get_mood_score') else 0.0
            )
        elif memory and hasattr(memory, 'events') and not is_survival_critical:
            memory.events.append({
                'time': current_time,
                'type': 'decision',
                'description': f"决定执行{intent.intent.name}",
                'impact': emotion.get_mood_score() * 0.3 if hasattr(emotion, 'get_mood_score') else 0.0
            })

    def _apply_emergency_modifiers(self, intent: IntentComponent, emotion: EmotionComponent, scores: dict):
        """生理紧急状态下的情绪微调（不覆盖生存意图）"""
        if not emotion:
            return
        
        # 极度恐惧时，即使口渴也可能先逃跑
        if emotion.fear > 0.8 and scores.get(IntentType.FLEE, 0) > scores.get(intent.intent, 0):
            intent.intent = IntentType.FLEE
            intent.priority = emotion.fear * 100
