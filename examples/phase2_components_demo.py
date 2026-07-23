#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:phase2_components_demo.py
@说明:Phase 2组件演示
@时间:2026/07/19
@版本:1.0
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import random
from core.world import World
from human.components.social.social_component_v4 import SocialManagerComponent, RelationshipType, InteractionType, SocialRole, SocialStatus
from human.components.cognitive.cognitive_component_v4 import CognitiveComponent, LearningStyle, DecisionStyle, RiskPreference
from human.components.perception.perception_component_v4 import PerceptionComponent, VisionType, HearingType, SpatialAwareness
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType
from space.space_component import SpaceComponent
from human.systems.social_system import SocialSystem
from human.systems.cognitive_system import CognitiveSystem
from human.systems.perception_system import PerceptionSystem

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_demo_world():
    """创建演示世界"""
    world = World()
    
    # 添加系统
    world.add_system(SocialSystem())
    world.add_system(CognitiveSystem())
    world.add_system(PerceptionSystem())
    
    return world


def create_human_entity(world, entity_id, name, x, y):
    """创建人类实体"""
    entity = world.create_entity()
    
    # 添加组件
    world.add_component(entity, HumanComponent())
    
    world.add_component(entity, SpaceComponent(x=x, y=y))
    
    world.add_component(entity, IntentComponent(
        intent=random.choice([IntentType.WORK, IntentType.SOCIALIZE, IntentType.EXPLORE, IntentType.BUILD])
    ))
    
    # 添加Phase 2组件
    world.add_component(entity, SocialManagerComponent())
    world.add_component(entity, CognitiveComponent())
    world.add_component(entity, PerceptionComponent())
    
    return entity


def demonstrate_social_system(world, entities):
    """演示社会系统"""
    print("\n=== 社会系统演示 ===")
    
    # 获取社会组件
    for entity_id in entities:
        entity = world.query_entity(entity_id)
        social = world.get_component(entity, SocialManagerComponent)
        
        if social:
            print(f"\n实体 {entity_id} 社会摘要:")
            summary = social.get_social_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")
    
    # 演示社会互动
    print("\n--- 演示社会互动 ---")
    entity1 = world.query_entity(entities[0])
    social1 = world.get_component(entity1, SocialManagerComponent)
    
    if social1 and len(entities) > 1:
        # 添加关系
        relationship_id = social1.add_relationship(entities[1], RelationshipType.FRIEND, strength=0.6)
        print(f"实体 {entities[0]} 与实体 {entities[1]} 建立友谊关系")
        
        # 添加互动
        interaction_id = social1.add_interaction(InteractionType.HELP, [entities[1], entities[2]])
        print(f"实体 {entities[0]} 开始帮助互动，涉及实体 {entities[1]} 和 {entities[2]}")
        
        # 完成互动
        social1.complete_interaction(interaction_id, outcome=0.8)
        print(f"互动完成，结果: 0.8")
        
        # 显示更新后的关系
        relationship = social1.get_relationship(entities[1])
        if relationship:
            print(f"关系强度更新为: {relationship.strength:.2f}")


def demonstrate_cognitive_system(world, entities):
    """演示认知系统"""
    print("\n=== 认知系统演示 ===")
    
    # 获取认知组件
    for entity_id in entities:
        entity = world.query_entity(entity_id)
        cognitive = world.get_component(entity, CognitiveComponent)
        
        if cognitive:
            print(f"\n实体 {entity_id} 认知摘要:")
            summary = cognitive.get_cognitive_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")
    
    # 演示学习
    print("\n--- 演示学习 ---")
    entity1 = world.query_entity(entities[0])
    cognitive1 = world.get_component(entity1, CognitiveComponent)
    
    if cognitive1:
        # 学习技能
        cognitive1.learn_skill("编程", practice_amount=0.3)
        proficiency = cognitive1.get_skill_proficiency("编程")
        print(f"实体 {entities[0]} 学习编程技能，熟练度: {proficiency:.2f}")
        
        # 添加知识
        cognitive1.add_knowledge("数学", level=0.7)
        knowledge_level = cognitive1.get_knowledge_level("数学")
        print(f"实体 {entities[0]} 学习数学知识，水平: {knowledge_level:.2f}")
        
        # 做出决策
        decision_id = cognitive1.make_decision("如何提高工作效率？", ["学习新技能", "优化流程", "寻求帮助"])
        decision = cognitive1.decision_history[-1]
        print(f"实体 {entities[0]} 做出决策: {decision.chosen_option}，置信度: {decision.confidence:.2f}")


def demonstrate_perception_system(world, entities):
    """演示感知系统"""
    print("\n=== 感知系统演示 ===")
    
    # 获取感知组件
    for entity_id in entities:
        entity = world.query_entity(entity_id)
        perception = world.get_component(entity, PerceptionComponent)
        
        if perception:
            print(f"\n实体 {entity_id} 感知摘要:")
            summary = perception.get_perception_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")
    
    # 演示感知更新
    print("\n--- 演示感知更新 ---")
    entity1 = world.query_entity(entities[0])
    perception1 = world.get_component(entity1, PerceptionComponent)
    
    if perception1:
        # 更新空间地图
        perception1.update_spatial_map((10, 10), 20.0)
        print(f"实体 {entities[0]} 更新空间地图，中心: (10, 10)，范围: 20.0")
        
        # 添加障碍物和资源
        perception1.add_obstacle((15, 15))
        perception1.add_resource((5, 5))
        print(f"实体 {entities[0]} 添加障碍物: (15, 15)，资源: (5, 5)")
        
        # 模拟视觉更新
        entities_info = [
            (2, (12, 12), 1.0, "brown", "human", (0, 0)),
            (3, (8, 8), 0.5, "gray", "rock", (0, 0))
        ]
        perception1.update_vision(entities_info)
        print(f"实体 {entities[0]} 视觉更新，可见实体数: {len(perception1.visible_entities)}")
        
        # 评估威胁和机会
        threat_level = perception1.assess_threats()
        opportunity_level = perception1.assess_opportunities()
        print(f"实体 {entities[0]} 威胁水平: {threat_level:.2f}，机会水平: {opportunity_level:.2f}")


def run_simulation(world, entities, steps=10):
    """运行模拟"""
    print(f"\n=== 运行模拟 ({steps} 步) ===")
    
    for step in range(steps):
        print(f"\n--- 步骤 {step + 1} ---")
        
        # 更新世界
        world.update(1.0)
        
        # 显示统计信息
        if step % 3 == 0:  # 每3步显示一次统计
            show_statistics(world, entities)


def show_statistics(world, entities):
    """显示统计信息"""
    print("\n统计信息:")
    
    # 社会统计
    social_system = None
    for system in world.systems:
        if isinstance(system, SocialSystem):
            social_system = system
            break
    
    if social_system:
        social_stats = social_system.get_social_statistics(world)
        print(f"  社会: {social_stats['total_entities']} 实体，{social_stats['total_relationships']} 关系")
    
    # 认知统计
    cognitive_system = None
    for system in world.systems:
        if isinstance(system, CognitiveSystem):
            cognitive_system = system
            break
    
    if cognitive_system:
        cognitive_stats = cognitive_system.get_cognitive_statistics(world)
        print(f"  认知: {cognitive_stats['total_skills']} 技能，{cognitive_stats['total_knowledge']} 知识")
    
    # 感知统计
    perception_system = None
    for system in world.systems:
        if isinstance(system, PerceptionSystem):
            perception_system = system
            break
    
    if perception_system:
        perception_stats = perception_system.get_perception_statistics(world)
        print(f"  感知: {perception_stats['total_visible_entities']} 可见实体，{perception_stats['total_audible_sounds']} 可听声音")


def main():
    """主函数"""
    print("=== Phase 2 组件演示 ===")
    
    # 创建世界
    world = create_demo_world()
    
    # 创建实体
    entities = []
    for i in range(5):
        entity_id = create_human_entity(world, i, f"人类{i}", random.uniform(0, 20), random.uniform(0, 20))
        entities.append(entity_id.id)
    
    print(f"创建了 {len(entities)} 个实体")
    
    # 演示各个系统
    demonstrate_social_system(world, entities)
    demonstrate_cognitive_system(world, entities)
    demonstrate_perception_system(world, entities)
    
    # 运行模拟
    run_simulation(world, entities, steps=15)
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    main()