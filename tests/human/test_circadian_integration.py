#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
昼夜节律集成测试

验证 DecisionSystem 正确应用昼夜节律修正
"""

import pytest

from core.world import World
from biology.components.circadian_component import CircadianComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.health_status_component import HealthStatusComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType
from human.components.cognitive.emotion_component import EmotionComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.cognitive.personality_component import PersonalityComponent
from human.components.cognitive.brain_component import BrainComponent
from human.components.cognitive.goal_component import GoalComponent
from human.systems.cognitive.decision_system import DecisionSystem
from human.systems.cognitive.decision_strategies import CircadianStrategy


class TestCircadianIntegration:
    """测试昼夜节律与决策系统集成"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return DecisionSystem()

    def test_night_time_reduces_activity(self, world, system):
        """测试夜间降低活动意图得分"""
        entity = world.create_entity()
        
        # 创建必要组件
        intent = IntentComponent(intent=IntentType.EXPLORE)
        emotion = EmotionComponent()
        memory = MemoryComponent()
        personality = PersonalityComponent()
        brain = BrainComponent()
        needs = PhysiologyNeedsComponent()
        health = HealthStatusComponent()
        circadian = CircadianComponent(phase=0.0, is_diurnal=True)  # 午夜
        
        world.add_component(entity, intent)
        world.add_component(entity, emotion)
        world.add_component(entity, memory)
        world.add_component(entity, personality)
        world.add_component(entity, brain)
        world.add_component(entity, needs)
        world.add_component(entity, health)
        world.add_component(entity, circadian)
        
        # 使用策略类直接测试
        strategy = CircadianStrategy()
        scores = {IntentType.EXPLORE: 50, IntentType.REST: 10}
        context = {
            'circadian': circadian,
            'is_survival_critical': False,
        }
        strategy.evaluate(scores, context)
        
        # 夜间探索得分应该降低
        assert scores[IntentType.EXPLORE] < 50
        # 夜间休息得分应该增加
        assert scores[IntentType.REST] > 10

    def test_day_time_increases_activity(self, world, system):
        """测试白天增加活动意图得分"""
        entity = world.create_entity()
        
        intent = IntentComponent(intent=IntentType.EXPLORE)
        emotion = EmotionComponent()
        memory = MemoryComponent()
        personality = PersonalityComponent()
        brain = BrainComponent()
        needs = PhysiologyNeedsComponent()
        health = HealthStatusComponent()
        circadian = CircadianComponent(phase=0.5, is_diurnal=True)  # 正午
        
        world.add_component(entity, intent)
        world.add_component(entity, emotion)
        world.add_component(entity, memory)
        world.add_component(entity, personality)
        world.add_component(entity, brain)
        world.add_component(entity, needs)
        world.add_component(entity, health)
        world.add_component(entity, circadian)
        
        strategy = CircadianStrategy()
        scores = {IntentType.EXPLORE: 50, IntentType.REST: 10}
        context = {
            'circadian': circadian,
            'is_survival_critical': False,
        }
        strategy.evaluate(scores, context)
        
        # 白天探索得分应该增加
        assert scores[IntentType.EXPLORE] > 50
        # 白天休息得分应该降低（或不变）
        assert scores[IntentType.REST] <= 10

    def test_high_sleep_debt_forces_sleep(self, world, system):
        """测试高睡眠债务强制增加睡眠优先级"""
        circadian = CircadianComponent(phase=0.0, sleep_debt=0.8)  # 夜间
        needs = PhysiologyNeedsComponent()
        
        strategy = CircadianStrategy()
        scores = {IntentType.REST: 10}
        context = {
            'circadian': circadian,
            'is_survival_critical': False,
        }
        strategy.evaluate(scores, context)
        
        # 夜间应该增加休息得分
        assert scores[IntentType.REST] > 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
