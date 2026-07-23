#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:test_enhanced_components.py
@说明:增强组件测试
@时间:2026/07/19
@版本:1.0
'''

import pytest
from core.world import World
from biology.components.physiology_needs_component_v3 import PhysiologyNeedsComponent, SleepStage
from human.components.health.health_component import HealthComponent, DiseaseType, InjuryType, TreatmentType, BodyPart
from human.components.cognitive.emotion_component_v4 import EmotionComponent, BasicEmotion, ComplexEmotion
from human.components.cognitive.memory_component_v4 import MemoryManagerComponent, MemoryType
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType


class TestPhysiologyNeedsComponent:
    """生理需求组件测试"""
    
    def test_physiology_needs_initialization(self):
        """测试生理需求组件初始化"""
        needs = PhysiologyNeedsComponent()
        
        # 检查基本需求
        assert needs.hunger == 0.0
        assert needs.thirst == 0.0
        assert needs.sleepiness == 0.0
        assert needs.fatigue == 0.0
        
        # 检查营养系统
        assert needs.protein == 0.5
        assert needs.carbohydrate == 0.5
        assert needs.fat == 0.5
        assert needs.vitamin == 0.5
        assert needs.mineral == 0.5
        
        # 检查代谢系统
        assert needs.basal_metabolic_rate == 1500.0
        assert needs.body_temperature == 37.0
        
        # 检查睡眠系统
        assert needs.sleep_stage == SleepStage.AWAKE
        assert needs.sleep_quality == 0.5
    
    def test_metabolism_update(self):
        """测试代谢更新"""
        needs = PhysiologyNeedsComponent()
        
        # 初始状态
        initial_glucose = needs.metabolic_state['glucose']
        
        # 更新代谢
        needs.update_metabolism(1.0, activity_level=1.0)
        
        # 检查血糖消耗
        assert needs.metabolic_state['glucose'] < initial_glucose
    
    def test_sleep_update(self):
        """测试睡眠更新"""
        needs = PhysiologyNeedsComponent()
        
        # 初始状态
        assert needs.sleep_stage == SleepStage.AWAKE
        assert needs.sleep_duration == 0.0
        
        # 更新睡眠（睡觉）
        needs.update_sleep(1.0, is_sleeping=True)
        
        # 检查睡眠状态
        assert needs.sleep_duration > 0.0
        assert needs.sleep_stage in [SleepStage.LIGHT, SleepStage.DEEP, SleepStage.REM]
        
        # 更新睡眠（清醒）
        needs.update_sleep(1.0, is_sleeping=False)
        
        # 检查清醒状态
        assert needs.sleep_stage == SleepStage.AWAKE
    
    def test_consume_food(self):
        """测试消耗食物"""
        needs = PhysiologyNeedsComponent()
        
        # 初始状态
        initial_protein = needs.protein
        initial_satiety = needs.satiety
        
        # 消耗食物
        needs.consume_food(protein=0.3, carbohydrate=0.4, fat=0.2, vitamin=0.1, mineral=0.1)
        
        # 检查营养补充
        assert needs.protein > initial_protein
        assert needs.satiety > initial_satiety
    
    def test_health_status(self):
        """测试健康状态"""
        needs = PhysiologyNeedsComponent()
        
        # 获取健康评分
        health_score = needs.get_overall_health()
        assert 0.0 <= health_score <= 1.0
        
        # 获取营养状态
        nutrition_status = needs.get_nutritional_status()
        assert nutrition_status in ["严重营养不良", "营养不良", "营养一般", "营养良好", "营养优秀"]
        
        # 获取睡眠状态
        sleep_status = needs.get_sleep_status()
        assert sleep_status in ["精神饱满", "轻微困倦", "非常困倦", "浅睡中", "深睡中", "快速眼动睡眠中"]
        
        # 获取疲劳状态
        fatigue_status = needs.get_fatigue_status()
        assert fatigue_status in ["精力充沛", "轻微疲劳", "中度疲劳", "极度疲劳"]


class TestHealthComponent:
    """健康组件测试"""
    
    def test_health_initialization(self):
        """测试健康组件初始化"""
        health = HealthComponent()
        
        # 检查整体健康
        assert health.overall_health == 1.0
        assert health.current_health == 100.0
        
        # 检查身体部位
        assert len(health.body_parts) == len(BodyPart)
        
        # 检查疾病和伤害
        assert len(health.diseases) == 0
        assert len(health.injuries) == 0
    
    def test_add_disease(self):
        """测试添加疾病"""
        health = HealthComponent()
        
        # 添加疾病
        disease_id = health.add_disease(
            DiseaseType.COMMON_COLD,
            "普通感冒",
            severity=0.5,
            symptoms=["咳嗽", "流鼻涕"],
            affected_parts=[BodyPart.HEAD, BodyPart.LUNGS]
        )
        
        # 检查疾病
        assert disease_id in health.diseases
        assert health.diseases[disease_id].name == "普通感冒"
        assert health.diseases[disease_id].severity == 0.5
        
        # 检查身体部位影响
        assert health.body_parts[BodyPart.HEAD].disease_level > 0.0
        assert health.body_parts[BodyPart.LUNGS].disease_level > 0.0
    
    def test_add_injury(self):
        """测试添加伤害"""
        health = HealthComponent()
        
        # 添加伤害
        injury_id = health.add_injury(
            InjuryType.CUT,
            BodyPart.LEFT_ARM,
            severity=0.6,
            pain_level=0.7
        )
        
        # 检查伤害
        assert injury_id in health.injuries
        assert health.injuries[injury_id].injury_type == InjuryType.CUT
        assert health.injuries[injury_id].severity == 0.6
        
        # 检查身体部位影响
        assert health.body_parts[BodyPart.LEFT_ARM].injury_level > 0.0
        assert health.body_parts[BodyPart.LEFT_ARM].pain_level > 0.0
    
    def test_apply_treatment(self):
        """测试应用治疗"""
        health = HealthComponent()
        
        # 添加疾病
        disease_id = health.add_disease(DiseaseType.COMMON_COLD, "普通感冒")
        
        # 应用治疗
        health.apply_treatment(TreatmentType.MEDICINE, disease_id)
        
        # 检查治疗
        assert TreatmentType.MEDICINE in health.active_treatments
        assert health.diseases[disease_id].treatment == TreatmentType.MEDICINE
    
    def test_health_update(self):
        """测试健康更新"""
        health = HealthComponent()
        
        # 添加疾病
        disease_id = health.add_disease(DiseaseType.COMMON_COLD, "普通感冒", severity=0.5)
        
        # 初始严重程度
        initial_severity = health.diseases[disease_id].severity
        
        # 更新健康
        health.update_health(1.0)
        
        # 检查疾病恢复
        assert health.diseases[disease_id].severity < initial_severity
    
    def test_health_status(self):
        """测试健康状态"""
        health = HealthComponent()
        
        # 获取健康评分
        health_score = health.get_overall_health_score()
        assert 0.0 <= health_score <= 1.0
        
        # 获取健康状态
        health_status = health.get_health_status()
        assert health_status in ["危重", "虚弱", "一般", "良好", "优秀"]
        
        # 获取健康摘要
        health_summary = health.get_health_summary()
        assert 'overall_health' in health_summary
        assert 'health_status' in health_summary
        assert 'diseases_count' in health_summary
        assert 'injuries_count' in health_summary


class TestEmotionComponent:
    """情绪组件测试"""
    
    def test_emotion_initialization(self):
        """测试情绪组件初始化"""
        emotion = EmotionComponent()
        
        # 检查基本情绪
        assert emotion.happiness == 0.5
        assert emotion.anger == 0.0
        assert emotion.fear == 0.0
        
        # 检查复合情绪
        assert emotion.satisfaction == 0.5
        assert emotion.hope == 0.5
        
        # 检查情绪状态
        assert emotion.mood == 0.5
        assert emotion.stress == 0.0
    
    def test_add_emotion(self):
        """测试添加情绪"""
        emotion = EmotionComponent()
        
        # 添加情绪
        emotion.add_emotion(BasicEmotion.HAPPINESS, 0.8, trigger="收到礼物")
        
        # 检查情绪
        assert emotion.happiness == 0.8
        assert "HAPPINESS" in emotion.current_emotions
        assert emotion.current_emotions["HAPPINESS"].intensity == 0.8
        assert emotion.current_emotions["HAPPINESS"].trigger == "收到礼物"
    
    def test_emotion_update(self):
        """测试情绪更新"""
        emotion = EmotionComponent()
        
        # 添加情绪
        emotion.add_emotion(BasicEmotion.HAPPINESS, 0.8)
        
        # 初始强度
        initial_intensity = emotion.happiness
        
        # 更新情绪
        emotion.update_emotions(1.0)
        
        # 检查情绪衰减
        assert emotion.happiness < initial_intensity
    
    def test_emotion_impact(self):
        """测试情绪影响"""
        emotion = EmotionComponent()
        
        # 设置情绪
        emotion.happiness = 0.8
        emotion.calmness = 0.7
        emotion.stress = 0.3
        
        # 获取行为影响
        behavior_impact = emotion.get_emotion_impact_on_behavior()
        assert 'decision_quality' in behavior_impact
        assert 'social_interaction' in behavior_impact
        assert 'work_efficiency' in behavior_impact
        
        # 获取健康影响
        health_impact = emotion.get_emotion_impact_on_health()
        assert 'immune_system' in health_impact
        assert 'recovery_rate' in health_impact
        assert 'sleep_quality' in health_impact
    
    def test_group_emotion(self):
        """测试群体情绪"""
        emotion = EmotionComponent()
        
        # 应用群体情绪
        group_emotion = {'happiness': 0.8, 'sadness': 0.2}
        emotion.apply_group_emotion(group_emotion, influence=0.5)
        
        # 检查情绪传染
        assert emotion.happiness > 0.5  # 向群体情绪靠拢
        assert emotion.group_emotion_influence == 0.5


class TestMemoryComponent:
    """记忆组件测试"""
    
    def test_memory_initialization(self):
        """测试记忆组件初始化"""
        memory = MemoryManagerComponent()
        
        # 检查记忆存储
        assert len(memory.working_memory) == 0
        assert len(memory.long_term_memory) == 0
        
        # 检查记忆容量
        assert memory.working_memory_capacity == 7
        assert memory.long_term_memory_capacity == 10000
        
        # 检查记忆统计
        assert memory.total_memories == 0
    
    def test_add_memory(self):
        """测试添加记忆"""
        memory = MemoryManagerComponent()
        
        # 添加记忆
        memory_id = memory.add_memory(
            MemoryType.EPISODIC,
            {'type': 'food', 'action': 'eat', 'satisfaction': 0.8},
            importance=0.6
        )
        
        # 检查记忆
        assert memory_id in memory.long_term_memory
        assert memory.long_term_memory[memory_id].memory_type == MemoryType.EPISODIC
        assert memory.long_term_memory[memory_id].importance == 0.6
        assert memory.total_memories == 1
    
    def test_working_memory(self):
        """测试工作记忆"""
        memory = MemoryManagerComponent()
        
        # 添加工作记忆
        memory_id = memory.add_memory(
            MemoryType.WORKING,
            {'type': 'task', 'action': 'work'},
            importance=0.5
        )
        
        # 检查工作记忆
        assert len(memory.working_memory) == 1
        assert memory.working_memory[0].memory_id == memory_id
    
    def test_retrieve_memory(self):
        """测试检索记忆"""
        memory = MemoryManagerComponent()
        
        # 添加记忆（使用高重要性确保检索成功）
        memory_id = memory.add_memory(
            MemoryType.SEMANTIC,
            {'type': 'knowledge', 'content': '水的化学式是H2O'},
            importance=0.9
        )
        
        # 手动设置记忆强度为高级别
        memory.long_term_memory[memory_id].strength = 0.8
        
        # 检索记忆
        retrieved_memory = memory.retrieve_memory(memory_id)
        
        # 检查检索
        assert retrieved_memory is not None
        assert retrieved_memory.memory_id == memory_id
        assert retrieved_memory.content['type'] == 'knowledge'
    
    def test_memory_update(self):
        """测试记忆更新"""
        memory = MemoryManagerComponent()
        
        # 添加记忆
        memory_id = memory.add_memory(
            MemoryType.EPISODIC,
            {'type': 'event', 'description': '重要事件'},
            importance=0.8
        )
        
        # 初始强度
        initial_strength = memory.long_term_memory[memory_id].strength
        
        # 更新记忆
        memory.update_memories(1.0)
        
        # 检查记忆强度变化
        assert memory.long_term_memory[memory_id].strength <= initial_strength
    
    def test_memory_consolidation(self):
        """测试记忆巩固"""
        memory = MemoryManagerComponent()
        
        # 添加工作记忆
        memory_id = memory.add_memory(
            MemoryType.WORKING,
            {'type': 'task', 'action': 'work'},
            importance=0.6
        )
        
        # 巩固记忆
        memory.consolidate_memories()
        
        # 检查工作记忆清空
        assert len(memory.working_memory) == 0
        
        # 检查长期记忆
        assert memory_id in memory.long_term_memory
    
    def test_memory_statistics(self):
        """测试记忆统计"""
        memory = MemoryManagerComponent()
        
        # 添加不同类型的记忆
        memory.add_memory(MemoryType.EPISODIC, {'type': 'event'}, importance=0.5)
        memory.add_memory(MemoryType.SEMANTIC, {'type': 'knowledge'}, importance=0.7)
        memory.add_memory(MemoryType.PROCEDURAL, {'type': 'skill'}, importance=0.8)
        
        # 获取统计
        stats = memory.get_memory_statistics()
        
        # 检查统计
        assert stats['total_memories'] == 3
        assert stats['memories_by_type']['EPISODIC'] == 1
        assert stats['memories_by_type']['SEMANTIC'] == 1
        assert stats['memories_by_type']['PROCEDURAL'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])