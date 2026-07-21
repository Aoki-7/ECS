#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:phase3_components_demo.py
@说明:Phase 3组件演示
@时间:2026/07/19
@版本:1.0
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import random
from core.world import World
from human.components.health.disease_component_v4 import DiseaseManagerComponent, DiseaseSeverity, TransmissionMode
from human.components.cognitive.education_component_v4 import EducationComponent, EducationLevel, TeachingMethod, LearningStyle, Course
from human.components.health.health_component import HealthComponent
from human.components.cognitive.cognitive_component_v4 import CognitiveComponent
from human.components.basic.human_component import HumanComponent
from human.components.social.social_component_v4 import SocialManagerComponent, RelationshipType
from space.space_component import SpaceComponent
from human.systems.disease_system import DiseaseSystem
from human.systems.education_system import EducationSystem

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_demo_world():
    """创建演示世界"""
    world = World()
    
    # 添加系统
    world.add_system(DiseaseSystem())
    world.add_system(EducationSystem())
    
    return world


def create_human_entity(world, entity_id, name, x, y):
    """创建人类实体"""
    entity = world.create_entity()
    
    # 添加组件
    world.add_component(entity, HumanComponent())
    world.add_component(entity, SpaceComponent(x=x, y=y))
    world.add_component(entity, HealthComponent())
    world.add_component(entity, DiseaseManagerComponent())
    world.add_component(entity, EducationComponent())
    world.add_component(entity, CognitiveComponent())
    world.add_component(entity, SocialManagerComponent())
    
    return entity


def demonstrate_disease_system(world, entities):
    """演示疾病系统"""
    print("\n=== 疾病系统演示 ===")
    
    # 获取疾病组件
    for entity_id in entities:
        entity = world.query_entity(entity_id)
        disease = world.get_component(entity, DiseaseManagerComponent)
        
        if disease:
            print(f"\n实体 {entity_id} 疾病摘要:")
            summary = disease.get_disease_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")
    
    # 演示疾病传播
    print("\n--- 演示疾病传播 ---")
    entity1 = world.query_entity(entities[0])
    disease1 = world.get_component(entity1, DiseaseManagerComponent)
    
    if disease1:
        # 添加疾病
        disease_id = disease1.add_disease("流感", DiseaseSeverity.MODERATE, TransmissionMode.AIRBORNE)
        print(f"实体 {entities[0]} 感染流感，疾病ID: {disease_id}")
        
        # 检查传染性
        flu = disease1.current_diseases[disease_id]
        print(f"流感传染性: {flu.infectivity}")
        print(f"流感传播概率: {flu.get_transmission_probability()}")
        
        # 模拟疾病进展
        current_time = 0.0
        flu.infection_time = current_time
        flu.stage_start_time = current_time
        
        # 推进到前驱期
        current_time = flu.incubation_period + 0.1
        disease1.update_disease_stage(disease_id, current_time)
        print(f"流感阶段: {flu.stage.name}")
        
        # 推进到急性期
        current_time = flu.incubation_period + 1.1
        disease1.update_disease_stage(disease_id, current_time)
        print(f"流感阶段: {flu.stage.name}")
        print(f"是否具有传染性: {flu.is_contagious()}")


def demonstrate_education_system(world, entities):
    """演示教育系统"""
    print("\n=== 教育系统演示 ===")
    
    # 获取教育组件
    for entity_id in entities:
        entity = world.query_entity(entity_id)
        education = world.get_component(entity, EducationComponent)
        
        if education:
            print(f"\n实体 {entity_id} 教育摘要:")
            summary = education.get_education_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")
    
    # 演示课程学习
    print("\n--- 演示课程学习 ---")
    entity1 = world.query_entity(entities[0])
    education1 = world.get_component(entity1, EducationComponent)
    
    if education1:
        # 创建课程
        course = Course(
            course_id=1,
            name="基础数学",
            subject="数学",
            level=EducationLevel.PRIMARY,
            teaching_method=TeachingMethod.LECTURE,
            duration=30.0,
            difficulty=0.3,
            knowledge_gain=0.2,
            skill_gain=0.1
        )
        
        # 注册课程
        record_id = education1.enroll_course(course, current_time=0.0)
        print(f"实体 {entities[0]} 注册课程: {course.name}")
        
        # 更新学习进度
        education1.update_learning_progress(record_id, 0.5, 15.0)
        print(f"学习进度: {education1.learning_records[record_id].progress}")
        
        # 完成课程
        education1.update_learning_progress(record_id, 0.5, 30.0)
        print(f"课程完成: {education1.learning_records[record_id].is_completed()}")
        print(f"教育水平: {education1.education_level.name}")
        
        # 添加知识和技能
        education1.add_knowledge("数学", 0.3)
        education1.add_skill("计算", 0.2)
        print(f"数学知识水平: {education1.get_knowledge_level('数学')}")
        print(f"计算技能水平: {education1.get_skill_level('计算')}")


def demonstrate_teaching_system(world, entities):
    """演示教学系统"""
    print("\n=== 教学系统演示 ===")
    
    # 设置一个实体为教师
    entity1 = world.query_entity(entities[0])
    education1 = world.get_component(entity1, EducationComponent)
    
    if education1:
        # 设置为教师
        education1.is_teacher = True
        education1.teaching_subjects = ["数学", "农业"]
        education1.teaching_ability = 0.8
        education1.add_knowledge("数学", 0.7)
        education1.add_knowledge("农业", 0.6)
        
        print(f"实体 {entities[0]} 成为教师")
        print(f"可教授学科: {education1.teaching_subjects}")
        print(f"教学能力: {education1.teaching_ability}")
        
        # 测试教学有效性
        effectiveness = education1.get_teaching_effectiveness(LearningStyle.VISUAL)
        print(f"对视觉学习者的教学有效性: {effectiveness}")
        
        # 为另一个实体注册课程
        entity2 = world.query_entity(entities[1])
        education2 = world.get_component(entity2, EducationComponent)
        
        if education2:
            # 创建课程
            course = Course(
                course_id=2,
                name="农业技术",
                subject="农业",
                level=EducationLevel.PRIMARY,
                teaching_method=TeachingMethod.PRACTICE,
                duration=45.0,
                difficulty=0.4,
                knowledge_gain=0.3,
                skill_gain=0.4
            )
            
            # 注册课程
            record_id = education2.enroll_course(course, teacher_id=entities[0], current_time=0.0)
            print(f"实体 {entities[1]} 在实体 {entities[0]} 指导下学习: {course.name}")
            
            # 建立师生关系
            social1 = world.get_component(entity1, SocialManagerComponent)
            social2 = world.get_component(entity2, SocialManagerComponent)
            
            if social1 and social2:
                social1.add_relationship(entities[1], RelationshipType.STUDENT, strength=0.6)
                social2.add_relationship(entities[0], RelationshipType.MENTOR, strength=0.6)
                print(f"建立师生关系: {entities[0]} (导师) - {entities[1]} (学生)")


def demonstrate_epidemic_scenario(world, entities):
    """演示流行病情景"""
    print("\n=== 流行病情景演示 ===")
    
    # 让多个实体感染同一种疾病
    disease_type = "瘟疫"
    infected_count = 0
    
    for i, entity_id in enumerate(entities):
        entity = world.query_entity(entity_id)
        disease = world.get_component(entity, DiseaseManagerComponent)
        
        if disease and i < 3:  # 前3个实体感染
            disease_id = disease.add_disease(disease_type, DiseaseSeverity.SEVERE, TransmissionMode.CONTACT)
            infected_count += 1
            print(f"实体 {entity_id} 感染{disease_type}")
    
    print(f"感染人数: {infected_count}/{len(entities)}")
    print(f"感染率: {infected_count/len(entities):.2%}")
    
    # 检查是否达到流行病阈值
    epidemic_threshold = 0.3  # 30%
    if infected_count / len(entities) >= epidemic_threshold:
        print(f"警告: {disease_type}已达到流行病水平!")


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
    
    # 疾病统计
    disease_system = None
    for system in world.systems:
        if isinstance(system, DiseaseSystem):
            disease_system = system
            break
    
    if disease_system:
        disease_stats = disease_system.get_disease_statistics(world)
        print(f"  疾病: {disease_stats['infected_entities']}/{disease_stats['total_entities']} 感染")
        print(f"  感染率: {disease_stats['infection_rate']:.2%}")
        if disease_stats['disease_type_distribution']:
            print(f"  疾病分布: {disease_stats['disease_type_distribution']}")
    
    # 教育统计
    education_system = None
    for system in world.systems:
        if isinstance(system, EducationSystem):
            education_system = system
            break
    
    if education_system:
        education_stats = education_system.get_education_statistics(world)
        print(f"  教育: {education_stats['teachers_count']} 教师, {education_stats['students_count']} 学生")
        if education_stats['education_level_distribution']:
            print(f"  教育水平: {education_stats['education_level_distribution']}")


def main():
    """主函数"""
    print("=== Phase 3 组件演示 ===")
    
    # 创建世界
    world = create_demo_world()
    
    # 创建实体
    entities = []
    for i in range(5):
        entity = create_human_entity(world, i, f"人类{i}", random.uniform(0, 20), random.uniform(0, 20))
        entities.append(entity.id)
    
    print(f"创建了 {len(entities)} 个实体")
    
    # 演示各个系统
    demonstrate_disease_system(world, entities)
    demonstrate_education_system(world, entities)
    demonstrate_teaching_system(world, entities)
    demonstrate_epidemic_scenario(world, entities)
    
    # 运行模拟
    run_simulation(world, entities, steps=15)
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    main()
