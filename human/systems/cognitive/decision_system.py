#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:decision_system.py
@说明:决策系统
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.0
'''

from core.system import System
from core.world import World

from human.components.cognitive.intent_component import IntentComponent, IntentType
from human.components.cognitive.emotion_component import EmotionComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.cognitive.personality_component import PersonalityComponent
from human.components.cognitive.brain_component import BrainComponent
from human.components.physiological.health_component import HealthComponent
from human.components.basic.age_component import AgeComponent


class DecisionSystem(System):
    """
    决策系统
    
    根据情绪、记忆、性格和当前意图，对行为进行优先级评估和决策。
    
    核心流程：
    1. 收集所有待决策的意图
    2. 根据情绪状态（恐惧、愤怒等）调整优先级
    3. 根据记忆中的过去经历学习
    4. 根据性格特征影响决策
    5. 最终确定采取哪个意图
    """

    def update(self, world: World, dt: float):
        """
        更新所有实体的决策状态
        
        Args:
            world: World实例
            dt: 时间增量
        """
        for entity, (intent, emotion, memory, personality, brain, health) in world.get_components(
            IntentComponent, EmotionComponent, MemoryComponent, PersonalityComponent, BrainComponent, HealthComponent
        ):
            self._make_decision(
                world, entity, 
                intent, emotion, memory, personality, brain, health,
                dt
            )

    def _make_decision(self, world: World, entity, 
                      intent: IntentComponent, emotion: EmotionComponent, 
                      memory: MemoryComponent, personality: PersonalityComponent,
                      brain: BrainComponent, health: HealthComponent, dt: float):
        """
        为单个实体做出决策
        
        Args:
            world: World实例
            entity: 实体ID
            intent: 意图组件
            emotion: 情绪组件
            memory: 记忆组件
            personality: 性格组件
            brain: 脑组件
            health: 健康组件
            dt: 时间增量
        """
        # 如果当前有活跃的意图，则暂时不改变
        if intent.intent != IntentType.IDLE and intent.urgency > 0:
            return
        
        # 计算各个意图的优先级
        intent_priorities = self._evaluate_intents(
            world, entity, emotion, memory, personality, health
        )
        
        # 选择优先级最高的意图
        if intent_priorities:
            best_intent = max(intent_priorities.items(), key=lambda x: x[1])
            intent.intent = best_intent[0]
            intent.urgency = best_intent[1]
            
            # 记录决策到脑组件
            if brain:
                brain.goal = str(best_intent[0])

    def _evaluate_intents(self, world: World, entity, 
                         emotion: EmotionComponent, memory: MemoryComponent,
                         personality: PersonalityComponent, health: HealthComponent) -> dict:
        """
        评估所有意图的优先级
        
        Args:
            world: World实例
            entity: 实体ID
            emotion: 情绪组件
            memory: 记忆组件
            personality: 性格组件
            health: 健康组件
            
        Returns:
            dict: {IntentType: priority_score}
        """
        priorities = {}
        
        # 基础优先级：根据健康状态
        base_priority = self._get_base_priority(world, entity, health)
        priorities.update(base_priority)
        
        # 情绪调整：根据当前情绪调整优先级
        emotion_adjustment = self._get_emotion_adjustment(emotion)
        for intent_type, adjustment in emotion_adjustment.items():
            if intent_type in priorities:
                priorities[intent_type] += adjustment
            else:
                priorities[intent_type] = adjustment
        
        # 性格调整：根据性格特征影响决策
        personality_adjustment = self._get_personality_adjustment(personality)
        for intent_type, adjustment in personality_adjustment.items():
            if intent_type in priorities:
                priorities[intent_type] += adjustment
            else:
                priorities[intent_type] = adjustment
        
        # 记忆学习：根据过去的经历调整
        memory_adjustment = self._get_memory_adjustment(memory)
        for intent_type, adjustment in memory_adjustment.items():
            if intent_type in priorities:
                priorities[intent_type] += adjustment
            else:
                priorities[intent_type] = adjustment
        
        # 过滤掉负优先级的意图
        priorities = {k: v for k, v in priorities.items() if v > 0}
        
        return priorities

    def _get_base_priority(self, world: World, entity, health: HealthComponent) -> dict:
        """
        获取基础优先级（根据生理和健康状态）
        
        Args:
            world: World实例
            entity: 实体ID
            health: 健康组件
            
        Returns:
            dict: {IntentType: priority}
        """
        priorities = {}
        
        # 获取生理需求组件
        from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
        needs = world.get_component(entity, PhysiologyNeedsComponent)
        
        if needs:
            # 饥饿驱动
            if needs.hunger > 70:
                priorities[IntentType.EAT] = 100.0
            elif needs.hunger > 40:
                priorities[IntentType.EAT] = 50.0
            
            # 口渴驱动
            if needs.thirst > 70:
                priorities[IntentType.DRINK] = 100.0
            elif needs.thirst > 40:
                priorities[IntentType.DRINK] = 50.0
            
            # 疲劳驱动
            if needs.energy < 20:
                priorities[IntentType.SLEEP] = 90.0
            elif needs.energy < 50:
                priorities[IntentType.REST] = 40.0
        
        # 健康驱动：低血量时优先治疗
        if health and health.hp < health.max_hp * 0.3:
            priorities[IntentType.HEAL] = 80.0
        
        # 安全驱动：逃离危险
        # （这里可以根据感知系统的数据来判断是否有危险）
        
        # 默认探索意图（如果没有其他驱动）
        if not priorities:
            priorities[IntentType.EXPLORE] = 10.0
        
        return priorities

    def _get_emotion_adjustment(self, emotion: EmotionComponent) -> dict:
        """
        根据情绪调整优先级
        
        情绪影响：
        - 恐惧 -> 优先逃离
        - 愤怒 -> 可能会攻击
        - 悲伤 -> 降低所有行为优先级
        - 快乐 -> 提升社交和探索
        
        Args:
            emotion: 情绪组件
            
        Returns:
            dict: {IntentType: adjustment}
        """
        adjustments = {}
        
        if not emotion:
            return adjustments
        
        # 恐惧
        if emotion.fear > 60:
            adjustments[IntentType.FLEE] = emotion.fear * 0.8
            # 恐惧时降低其他活动的优先级
            adjustments[IntentType.EXPLORE] = -30.0
            adjustments[IntentType.WORK] = -30.0
        
        # 愤怒
        if emotion.anger > 60:
            # 愤怒时可能会寻求冲突
            adjustments[IntentType.FLEE] = -40.0  # 不太可能逃离
        
        # 悲伤
        if emotion.sadness > 60:
            # 悲伤会降低积极行为的优先级
            adjustments[IntentType.EXPLORE] = -30.0
            adjustments[IntentType.WORK] = -30.0
            adjustments[IntentType.COLLECT] = -20.0
        
        # 快乐
        if emotion.joy > 60:
            # 快乐时更倾向于社交和探索
            adjustments[IntentType.EXPLORE] = 20.0
        
        return adjustments

    def _get_personality_adjustment(self, personality: PersonalityComponent) -> dict:
        """
        根据性格特征调整决策
        
        性格影响：
        - 开放性高 -> 更倾向探索
        - 谨慎性高 -> 更倾向躲藏和休息
        - 外向性高 -> 更倾向社交
        - 认真性高 -> 更倾向工作
        
        Args:
            personality: 性格组件
            
        Returns:
            dict: {IntentType: adjustment}
        """
        adjustments = {}
        
        if not personality:
            return adjustments
        
        # 开放性：对新事物和探索的兴趣
        if personality.openness > 70:
            adjustments[IntentType.EXPLORE] = 20.0
            adjustments[IntentType.COLLECT] = 15.0
        elif personality.openness < 30:
            adjustments[IntentType.EXPLORE] = -15.0
            adjustments[IntentType.COLLECT] = -10.0
        
        # 谨慎性：对风险的态度
        if personality.conscientiousness > 70:
            adjustments[IntentType.HIDE] = 10.0
            adjustments[IntentType.REST] = 15.0
        elif personality.conscientiousness < 30:
            adjustments[IntentType.FLEE] = -20.0
        
        # 外向性：对社交的渴望
        if personality.extraversion > 70:
            adjustments[IntentType.PAIR] = 25.0
        elif personality.extraversion < 30:
            adjustments[IntentType.PAIR] = -20.0
        
        # 认真性：对任务的态度
        if personality.conscientiousness > 70:
            adjustments[IntentType.WORK] = 20.0
            adjustments[IntentType.BUILD] = 15.0
        elif personality.conscientiousness < 30:
            adjustments[IntentType.WORK] = -15.0
            adjustments[IntentType.BUILD] = -15.0
        
        return adjustments

    def _get_memory_adjustment(self, memory: MemoryComponent) -> dict:
        """
        根据记忆学习调整决策
        
        记忆影响：
        - 最近做过什么会影响行为
        - 过去的负面经历会改变决策
        - 长期目标会指导行为
        
        Args:
            memory: 记忆组件
            
        Returns:
            dict: {IntentType: adjustment}
        """
        adjustments = {}
        
        if not memory:
            return adjustments
        
        # 根据最近的行动记录调整（简化实现）
        # 实际应该根据memory.recent_actions等字段进行更复杂的分析
        
        return adjustments
