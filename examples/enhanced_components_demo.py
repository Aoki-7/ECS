#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:enhanced_components_demo.py
@说明:增强组件演示脚本
@时间:2026/07/19
@版本:1.0
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from core.world import World
from biology.components.physiology_needs_component_v3 import PhysiologyNeedsComponent, SleepStage
from human.components.health.health_component import HealthComponent, DiseaseType, InjuryType, TreatmentType, BodyPart
from human.components.cognitive.emotion_component_v4 import EmotionComponent, BasicEmotion, ComplexEmotion
from human.components.cognitive.memory_component_v4 import MemoryManagerComponent, MemoryType
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_physiology_needs():
    """演示生理需求组件"""
    logger.info("=== 生理需求组件演示 ===")
    
    # 创建生理需求组件
    needs = PhysiologyNeedsComponent()
    
    # 显示初始状态
    logger.info(f"初始健康评分: {needs.get_overall_health():.2f}")
    logger.info(f"营养状态: {needs.get_nutritional_status()}")
    logger.info(f"睡眠状态: {needs.get_sleep_status()}")
    logger.info(f"疲劳状态: {needs.get_fatigue_status()}")
    
    # 模拟活动
    logger.info("\n--- 模拟高强度活动 ---")
    for i in range(5):
        needs.update_metabolism(1.0, activity_level=1.0)
        needs.hunger += 0.1
        needs.thirst += 0.15
        needs.muscle_fatigue += 0.2
    
    logger.info(f"活动后健康评分: {needs.get_overall_health():.2f}")
    logger.info(f"血糖水平: {needs.metabolic_state['glucose']:.2f}")
    logger.info(f"肌肉疲劳: {needs.muscle_fatigue:.2f}")
    
    # 进食
    logger.info("\n--- 进食 ---")
    needs.consume_food(protein=0.3, carbohydrate=0.4, fat=0.2, vitamin=0.1, mineral=0.1)
    logger.info(f"进食后营养状态: {needs.get_nutritional_status()}")
    logger.info(f"饱腹感: {needs.satiety:.2f}")
    
    # 睡眠
    logger.info("\n--- 睡眠 ---")
    for i in range(8):  # 睡眠8小时
        needs.update_sleep(1.0, is_sleeping=True)
    
    logger.info(f"睡眠后睡眠状态: {needs.get_sleep_status()}")
    logger.info(f"睡眠质量: {needs.sleep_quality:.2f}")
    logger.info(f"肌肉疲劳: {needs.muscle_fatigue:.2f}")


def demo_health():
    """演示健康组件"""
    logger.info("\n=== 健康组件演示 ===")
    
    # 创建健康组件
    health = HealthComponent()
    
    # 显示初始状态
    logger.info(f"初始健康状态: {health.get_health_status()}")
    logger.info(f"整体健康评分: {health.get_overall_health_score():.2f}")
    
    # 添加疾病
    logger.info("\n--- 感染疾病 ---")
    disease_id = health.add_disease(
        DiseaseType.COMMON_COLD,
        "普通感冒",
        severity=0.6,
        symptoms=["咳嗽", "流鼻涕", "喉咙痛"],
        affected_parts=[BodyPart.HEAD, BodyPart.LUNGS]
    )
    
    logger.info(f"感染疾病: {health.diseases[disease_id].name}")
    logger.info(f"疾病严重程度: {health.diseases[disease_id].severity:.2f}")
    logger.info(f"症状: {', '.join(health.diseases[disease_id].symptoms)}")
    logger.info(f"健康状态: {health.get_health_status()}")
    
    # 添加伤害
    logger.info("\n--- 受伤 ---")
    injury_id = health.add_injury(
        InjuryType.CUT,
        BodyPart.LEFT_ARM,
        severity=0.5,
        pain_level=0.7
    )
    
    logger.info(f"受伤: {health.injuries[injury_id].injury_type.name} at {health.injuries[injury_id].body_part.name}")
    logger.info(f"伤害严重程度: {health.injuries[injury_id].severity:.2f}")
    logger.info(f"疼痛程度: {health.injuries[injury_id].pain_level:.2f}")
    logger.info(f"健康状态: {health.get_health_status()}")
    
    # 治疗
    logger.info("\n--- 治疗 ---")
    health.apply_treatment(TreatmentType.MEDICINE, disease_id)
    health.apply_treatment(TreatmentType.BANDAGE, injury_id)
    
    logger.info(f"接受治疗: {[t.name for t in health.active_treatments]}")
    
    # 更新健康
    logger.info("\n--- 恢复健康 ---")
    for i in range(10):  # 恢复10小时
        health.update_health(1.0)
    
    logger.info(f"恢复后健康状态: {health.get_health_status()}")
    logger.info(f"疾病严重程度: {health.diseases[disease_id].severity:.2f}")
    if injury_id in health.injuries:
        logger.info(f"伤害愈合进度: {health.injuries[injury_id].healing_progress:.2f}")
    else:
        logger.info("伤害已完全愈合")
    
    # 健康摘要
    logger.info("\n--- 健康摘要 ---")
    summary = health.get_health_summary()
    for key, value in summary.items():
        logger.info(f"{key}: {value}")


def demo_emotion():
    """演示情绪组件"""
    logger.info("\n=== 情绪组件演示 ===")
    
    # 创建情绪组件
    emotion = EmotionComponent()
    
    # 显示初始状态
    logger.info(f"初始情绪状态: {emotion.get_emotional_state()}")
    logger.info(f"整体心情: {emotion.get_overall_mood():.2f}")
    
    # 添加情绪
    logger.info("\n--- 添加情绪 ---")
    emotion.add_emotion(BasicEmotion.HAPPINESS, 0.8, trigger="收到礼物")
    emotion.add_emotion(ComplexEmotion.EXCITEMENT, 0.7, trigger="期待旅行")
    
    logger.info(f"添加情绪后: {emotion.get_emotional_state()}")
    logger.info(f"快乐程度: {emotion.happiness:.2f}")
    logger.info(f"兴奋程度: {emotion.excitement:.2f}")
    logger.info(f"当前情绪: {list(emotion.current_emotions.keys())}")
    
    # 情绪影响
    logger.info("\n--- 情绪影响 ---")
    behavior_impact = emotion.get_emotion_impact_on_behavior()
    logger.info(f"决策质量: {behavior_impact['decision_quality']:.2f}")
    logger.info(f"社交互动: {behavior_impact['social_interaction']:.2f}")
    logger.info(f"工作效率: {behavior_impact['work_efficiency']:.2f}")
    
    # 群体情绪
    logger.info("\n--- 群体情绪影响 ---")
    group_emotion = {'happiness': 0.9, 'sadness': 0.1}
    emotion.apply_group_emotion(group_emotion, influence=0.5)
    
    logger.info(f"群体情绪影响后快乐程度: {emotion.happiness:.2f}")
    logger.info(f"群体情绪影响: {emotion.group_emotion_influence:.2f}")
    
    # 情绪更新
    logger.info("\n--- 情绪更新 ---")
    for i in range(5):  # 更新5小时
        emotion.update_emotions(1.0)
    
    logger.info(f"更新后快乐程度: {emotion.happiness:.2f}")
    logger.info(f"更新后兴奋程度: {emotion.excitement:.2f}")
    
    # 情绪摘要
    logger.info("\n--- 情绪摘要 ---")
    summary = emotion.get_emotional_summary()
    for key, value in summary.items():
        logger.info(f"{key}: {value}")


def demo_memory():
    """演示记忆组件"""
    logger.info("\n=== 记忆组件演示 ===")
    
    # 创建记忆组件
    memory = MemoryManagerComponent()
    
    # 显示初始状态
    logger.info(f"初始记忆统计: {memory.get_memory_statistics()}")
    
    # 添加记忆
    logger.info("\n--- 添加记忆 ---")
    food_memory_id = memory.add_memory(
        MemoryType.EPISODIC,
        {'type': 'food', 'action': 'eat', 'food': '苹果', 'satisfaction': 0.8},
        importance=0.6
    )
    
    knowledge_memory_id = memory.add_memory(
        MemoryType.SEMANTIC,
        {'type': 'knowledge', 'content': '水的化学式是H2O'},
        importance=0.9
    )
    
    skill_memory_id = memory.add_memory(
        MemoryType.PROCEDURAL,
        {'type': 'skill', 'skill_type': '烹饪', 'proficiency': 0.7},
        importance=0.8
    )
    
    logger.info(f"添加食物记忆: {food_memory_id}")
    logger.info(f"添加知识记忆: {knowledge_memory_id}")
    logger.info(f"添加技能记忆: {skill_memory_id}")
    logger.info(f"记忆统计: {memory.get_memory_statistics()}")
    
    # 检索记忆
    logger.info("\n--- 检索记忆 ---")
    retrieved_memory = memory.retrieve_memory(knowledge_memory_id)
    if retrieved_memory:
        logger.info(f"检索到记忆: {retrieved_memory.content['content']}")
        logger.info(f"记忆强度: {retrieved_memory.strength:.2f}")
    
    # 搜索记忆
    logger.info("\n--- 搜索记忆 ---")
    food_memories = memory.search_memories({'type': 'food'}, MemoryType.EPISODIC)
    logger.info(f"找到 {len(food_memories)} 个食物记忆")
    
    # 记忆巩固
    logger.info("\n--- 记忆巩固 ---")
    working_memory_id = memory.add_memory(
        MemoryType.WORKING,
        {'type': 'task', 'action': 'work', 'task': '写报告'},
        importance=0.5
    )
    
    logger.info(f"添加工作记忆: {working_memory_id}")
    logger.info(f"工作记忆数量: {len(memory.working_memory)}")
    
    memory.consolidate_memories()
    logger.info(f"巩固后工作记忆数量: {len(memory.working_memory)}")
    logger.info(f"巩固后长期记忆数量: {len(memory.long_term_memory)}")
    
    # 记忆更新
    logger.info("\n--- 记忆更新 ---")
    for i in range(10):  # 更新10小时
        memory.update_memories(1.0)
    
    logger.info(f"更新后记忆统计: {memory.get_memory_statistics()}")
    
    # 记忆摘要
    logger.info("\n--- 记忆摘要 ---")
    summary = memory.get_memory_summary()
    for key, value in summary.items():
        logger.info(f"{key}: {value}")


def demo_integration():
    """演示集成使用"""
    logger.info("\n=== 集成使用演示 ===")
    
    # 创建世界
    world = World()
    
    # 创建实体
    entity_id = world.create_entity()
    
    # 添加组件
    world.add_component(entity_id, HumanComponent())
    world.add_component(entity_id, SpaceComponent(x=0, y=0))
    world.add_component(entity_id, IntentComponent())
    world.add_component(entity_id, PhysiologyNeedsComponent())
    world.add_component(entity_id, HealthComponent())
    world.add_component(entity_id, EmotionComponent())
    world.add_component(entity_id, MemoryManagerComponent())
    
    # 获取组件
    needs = world.get_component(entity_id, PhysiologyNeedsComponent)
    health = world.get_component(entity_id, HealthComponent)
    emotion = world.get_component(entity_id, EmotionComponent)
    memory = world.get_component(entity_id, MemoryManagerComponent)
    
    # 模拟生活
    logger.info("--- 模拟一天的生活 ---")
    
    # 早上醒来
    logger.info("\n早上醒来:")
    needs.update_sleep(1.0, is_sleeping=False)
    logger.info(f"睡眠状态: {needs.get_sleep_status()}")
    logger.info(f"疲劳状态: {needs.get_fatigue_status()}")
    
    # 吃早餐
    logger.info("\n吃早餐:")
    needs.consume_food(protein=0.2, carbohydrate=0.3, fat=0.1, vitamin=0.1, mineral=0.1)
    emotion.add_emotion(BasicEmotion.HAPPINESS, 0.6, trigger="美味的早餐")
    memory.add_memory(MemoryType.EPISODIC, {'type': 'food', 'food': '早餐'}, importance=0.5)
    logger.info(f"营养状态: {needs.get_nutritional_status()}")
    logger.info(f"情绪状态: {emotion.get_emotional_state()}")
    
    # 工作
    logger.info("\n工作:")
    intent = world.get_component(entity_id, IntentComponent)
    intent.intent = IntentType.WORK
    needs.update_metabolism(4.0, activity_level=0.7)  # 工作4小时
    needs.mental_fatigue += 0.3
    emotion.add_emotion(ComplexEmotion.FRUSTRATION, 0.4, trigger="工作压力")
    memory.add_memory(MemoryType.EPISODIC, {'type': 'work', 'task': '项目'}, importance=0.6)
    logger.info(f"精神疲劳: {needs.mental_fatigue:.2f}")
    logger.info(f"情绪状态: {emotion.get_emotional_state()}")
    
    # 午餐
    logger.info("\n午餐:")
    needs.consume_food(protein=0.3, carbohydrate=0.4, fat=0.2, vitamin=0.1, mineral=0.1)
    emotion.add_emotion(BasicEmotion.HAPPINESS, 0.5, trigger="美味的午餐")
    logger.info(f"营养状态: {needs.get_nutritional_status()}")
    
    # 运动
    logger.info("\n运动:")
    needs.update_metabolism(1.0, activity_level=1.0)  # 运动1小时
    needs.muscle_fatigue += 0.4
    emotion.add_emotion(ComplexEmotion.SATISFACTION, 0.7, trigger="运动后的满足感")
    logger.info(f"肌肉疲劳: {needs.muscle_fatigue:.2f}")
    logger.info(f"情绪状态: {emotion.get_emotional_state()}")
    
    # 受伤
    logger.info("\n意外受伤:")
    injury_id = health.add_injury(InjuryType.BRUISE, BodyPart.LEFT_LEG, severity=0.3, pain_level=0.4)
    emotion.add_emotion(BasicEmotion.FEAR, 0.6, trigger="意外受伤")
    memory.add_memory(MemoryType.EMOTIONAL, {'type': 'injury', 'pain': 0.4}, importance=0.7, emotional_valence=-0.5)
    logger.info(f"健康状态: {health.get_health_status()}")
    logger.info(f"情绪状态: {emotion.get_emotional_state()}")
    
    # 治疗
    logger.info("\n治疗:")
    health.apply_treatment(TreatmentType.BANDAGE, injury_id)
    emotion.add_emotion(ComplexEmotion.HOPE, 0.5, trigger="得到治疗")
    logger.info(f"接受治疗: {[t.name for t in health.active_treatments]}")
    
    # 晚餐
    logger.info("\n晚餐:")
    needs.consume_food(protein=0.3, carbohydrate=0.3, fat=0.2, vitamin=0.2, mineral=0.1)
    emotion.add_emotion(BasicEmotion.HAPPINESS, 0.6, trigger="美味的晚餐")
    logger.info(f"营养状态: {needs.get_nutritional_status()}")
    
    # 社交
    logger.info("\n社交:")
    emotion.add_emotion(BasicEmotion.HAPPINESS, 0.8, trigger="与朋友聚会")
    emotion.loneliness = max(0.0, emotion.loneliness - 0.5)
    memory.add_memory(MemoryType.EPISODIC, {'type': 'social', 'activity': '聚会'}, importance=0.7)
    logger.info(f"情绪状态: {emotion.get_emotional_state()}")
    logger.info(f"孤独感: {emotion.loneliness:.2f}")
    
    # 睡觉
    logger.info("\n睡觉:")
    for i in range(8):  # 睡眠8小时
        needs.update_sleep(1.0, is_sleeping=True)
        health.update_health(1.0)
        emotion.update_emotions(1.0)
        memory.update_memories(1.0)
    
    logger.info(f"睡眠状态: {needs.get_sleep_status()}")
    logger.info(f"睡眠质量: {needs.sleep_quality:.2f}")
    logger.info(f"健康状态: {health.get_health_status()}")
    logger.info(f"情绪状态: {emotion.get_emotional_state()}")
    logger.info(f"记忆统计: {memory.get_memory_statistics()}")
    
    # 记忆巩固
    logger.info("\n记忆巩固:")
    memory.consolidate_memories()
    logger.info(f"巩固后记忆统计: {memory.get_memory_statistics()}")
    
    # 一天总结
    logger.info("\n--- 一天总结 ---")
    logger.info(f"整体健康: {needs.get_overall_health():.2f}")
    logger.info(f"健康状态: {health.get_health_status()}")
    logger.info(f"情绪状态: {emotion.get_emotional_state()}")
    logger.info(f"记忆数量: {memory.get_memory_statistics()['total_memories']}")


def main():
    """主函数"""
    logger.info("开始增强组件演示")
    
    # 演示各个组件
    demo_physiology_needs()
    demo_health()
    demo_emotion()
    demo_memory()
    demo_integration()
    
    logger.info("\n增强组件演示完成")


if __name__ == "__main__":
    main()