#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:test_phase3_components.py
@说明:Phase 3组件测试
@时间:2026/07/19
@版本:1.0
'''

import pytest
import random
from core.world import World
from human.components.health.disease_component_v4 import DiseaseManagerComponent, DiseaseSeverity, TransmissionMode, DiseaseStage
from human.components.cognitive.education_component_v4 import EducationComponent, EducationLevel, TeachingMethod, LearningStyle
from human.components.health.health_component import HealthComponent
from human.components.cognitive.cognitive_component_v4 import CognitiveComponent
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent


class TestDiseaseComponent:
    """疾病组件测试"""
    
    def test_disease_initialization(self):
        """测试疾病组件初始化"""
        disease = DiseaseManagerComponent()
        
        # 检查当前疾病
        assert len(disease.current_diseases) == 0
        assert disease.next_disease_id == 0
        
        # 检查免疫状态
        assert len(disease.immunities) == 0
        assert disease.natural_immunity == 0.5
        assert disease.acquired_immunity == 0.3
        
        # 检查易感性
        assert len(disease.susceptibility) == 0
        assert disease.base_susceptibility == 0.5
        
        # 检查治疗
        assert not disease.under_treatment
        assert disease.treatment_effectiveness == 0.0
        
        # 检查隔离
        assert not disease.quarantined
        assert disease.quarantine_start_time == 0.0
        
        # 检查历史
        assert len(disease.disease_history) == 0
    
    def test_add_disease(self):
        """测试添加疾病"""
        disease = DiseaseManagerComponent()
        
        # 添加流感
        disease_id = disease.add_disease("流感", DiseaseSeverity.MODERATE, TransmissionMode.AIRBORNE)
        
        # 检查疾病
        assert disease_id in disease.current_diseases
        flu = disease.current_diseases[disease_id]
        assert flu.disease_type == "流感"
        assert flu.severity == DiseaseSeverity.MODERATE
        assert flu.transmission_mode == TransmissionMode.AIRBORNE
        assert flu.stage == DiseaseStage.INCUBATION
        assert flu.infectivity == 0.7
        assert flu.mortality_rate == 0.001
        
        # 添加瘟疫
        plague_id = disease.add_disease("瘟疫", DiseaseSeverity.SEVERE, TransmissionMode.CONTACT)
        
        # 检查疾病
        assert plague_id in disease.current_diseases
        plague = disease.current_diseases[plague_id]
        assert plague.disease_type == "瘟疫"
        assert plague.severity == DiseaseSeverity.SEVERE
        assert plague.infectivity == 0.9
        assert plague.mortality_rate == 0.3
    
    def test_disease_stage_progression(self):
        """测试疾病阶段进展"""
        disease = DiseaseManagerComponent()
        
        # 添加疾病
        disease_id = disease.add_disease("流感", DiseaseSeverity.MODERATE, TransmissionMode.AIRBORNE)
        flu = disease.current_diseases[disease_id]
        
        # 设置感染时间
        infection_time = 0.0
        flu.infection_time = infection_time
        flu.stage_start_time = infection_time
        
        # 检查初始阶段
        assert flu.stage == DiseaseStage.INCUBATION
        
        # 模拟时间推进到潜伏期结束
        current_time = infection_time + flu.incubation_period + 0.1
        disease.update_disease_stage(disease_id, current_time)
        
        # 检查阶段是否推进到前驱期
        assert flu.stage == DiseaseStage.PRODROMAL
        
        # 模拟时间推进到前驱期结束
        current_time = infection_time + flu.incubation_period + 1.1
        disease.update_disease_stage(disease_id, current_time)
        
        # 检查阶段是否推进到急性期
        assert flu.stage == DiseaseStage.ACUTE
    
    def test_disease_recovery(self):
        """测试疾病康复"""
        disease = DiseaseManagerComponent()
        
        # 添加疾病
        disease_id = disease.add_disease("流感", DiseaseSeverity.MODERATE, TransmissionMode.AIRBORNE)
        
        # 康复
        recovery_time = 10.0
        disease.recover_from_disease(disease_id, recovery_time)
        
        # 检查疾病是否被移除
        assert disease_id not in disease.current_diseases
        
        # 检查免疫力
        assert "流感" in disease.immunities
        assert disease.immunities["流感"] > 0
        
        # 检查历史记录
        assert len(disease.disease_history) == 1
        assert disease.disease_history[0]['disease_type'] == "流感"
    
    def test_immunity_system(self):
        """测试免疫系统"""
        disease = DiseaseManagerComponent()
        
        # 添加免疫力
        disease.immunities["流感"] = 10.0
        
        # 检查是否免疫
        assert disease.is_immune_to("流感")
        assert not disease.is_immune_to("瘟疫")
        
        # 检查感染概率
        assert disease.get_infection_probability("流感") == 0.0
        assert disease.get_infection_probability("瘟疫") > 0.0
        
        # 更新免疫力
        disease.update_immunities(5.0)
        assert disease.immunities["流感"] == 5.0
        
        # 更新免疫力到过期
        disease.update_immunities(5.0)
        assert "流感" not in disease.immunities
    
    def test_disease_summary(self):
        """测试疾病摘要"""
        disease = DiseaseManagerComponent()
        
        # 添加一些数据
        disease.add_disease("流感", DiseaseSeverity.MODERATE, TransmissionMode.AIRBORNE)
        disease.immunities["瘟疫"] = 15.0
        disease.under_treatment = True
        
        # 获取疾病摘要
        summary = disease.get_disease_summary()
        
        # 检查摘要
        assert summary['current_diseases_count'] == 1
        assert "流感" in summary['current_diseases']
        assert summary['immunities_count'] == 1
        assert summary['under_treatment'] == True
        assert summary['quarantined'] == False


class TestEducationComponent:
    """教育组件测试"""
    
    def test_education_initialization(self):
        """测试教育组件初始化"""
        education = EducationComponent()
        
        # 检查教育水平
        assert education.education_level == EducationLevel.ILLITERATE
        assert len(education.subjects_studied) == 0
        
        # 检查学习能力
        assert education.learning_style == LearningStyle.VISUAL
        assert education.learning_ability == 0.5
        assert education.intelligence == 0.5
        
        # 检查学习记录
        assert len(education.learning_records) == 0
        assert education.next_record_id == 0
        assert education.current_course_id is None
        
        # 检查知识和技能
        assert len(education.knowledge) == 0
        assert len(education.skills) == 0
        
        # 检查教学能力
        assert not education.is_teacher
        assert len(education.teaching_subjects) == 0
        assert education.teaching_ability == 0.5
        
        # 检查教育历史
        assert len(education.education_history) == 0
    
    def test_add_knowledge_and_skill(self):
        """测试添加知识和技能"""
        education = EducationComponent()
        
        # 添加知识
        education.add_knowledge("数学", 0.3)
        education.add_knowledge("农业", 0.5)
        
        # 检查知识
        assert education.get_knowledge_level("数学") == 0.3
        assert education.get_knowledge_level("农业") == 0.5
        assert "数学" in education.subjects_studied
        assert "农业" in education.subjects_studied
        
        # 添加技能
        education.add_skill("种植", 0.4)
        education.add_skill("计算", 0.2)
        
        # 检查技能
        assert education.get_skill_level("种植") == 0.4
        assert education.get_skill_level("计算") == 0.2
    
    def test_course_enrollment(self):
        """测试课程注册"""
        education = EducationComponent()
        
        # 创建课程
        from human.components.cognitive.education_component_v4 import Course
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
        record_id = education.enroll_course(course, current_time=0.0)
        
        # 检查学习记录
        assert record_id in education.learning_records
        assert education.current_course_id == 1
        
        record = education.learning_records[record_id]
        assert record.course_id == 1
        assert record.progress == 0.0
        assert not record.is_completed()
    
    def test_learning_progress(self):
        """测试学习进度"""
        education = EducationComponent()
        
        # 创建课程
        from human.components.cognitive.education_component_v4 import Course
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
        record_id = education.enroll_course(course, current_time=0.0)
        
        # 更新学习进度
        education.update_learning_progress(record_id, 0.5, 15.0)
        
        # 检查进度
        record = education.learning_records[record_id]
        assert record.progress == 0.5
        assert not record.is_completed()
        
        # 完成课程
        education.update_learning_progress(record_id, 0.5, 30.0)
        
        # 检查完成状态
        assert record.progress == 1.0
        assert record.is_completed()
        assert record.completion_time == 30.0
        
        # 检查教育历史
        assert len(education.education_history) == 1
        assert education.education_history[0]['course_id'] == 1
    
    def test_teaching_ability(self):
        """测试教学能力"""
        education = EducationComponent()
        
        # 设置为教师
        education.is_teacher = True
        education.teaching_subjects = ["数学", "农业"]
        education.teaching_ability = 0.8
        
        # 检查是否能教授学科
        assert education.can_teach("数学")
        assert education.can_teach("农业")
        assert not education.can_teach("工艺")
        
        # 获取教学有效性
        effectiveness = education.get_teaching_effectiveness(LearningStyle.VISUAL)
        assert 0.0 <= effectiveness <= 1.0
        
        # 非教师教学有效性应为0
        education.is_teacher = False
        assert education.get_teaching_effectiveness(LearningStyle.VISUAL) == 0.0
    
    def test_education_level_progression(self):
        """测试教育水平进展"""
        education = EducationComponent()
        
        # 初始为文盲
        assert education.education_level == EducationLevel.ILLITERATE
        
        # 完成1门课程
        from human.components.cognitive.education_component_v4 import Course
        course1 = Course(1, "课程1", "学科1", EducationLevel.PRIMARY, TeachingMethod.LECTURE)
        record_id1 = education.enroll_course(course1, current_time=0.0)
        education.update_learning_progress(record_id1, 1.0, 30.0)
        
        # 检查教育水平
        assert education.education_level == EducationLevel.PRIMARY
        
        # 完成更多课程
        for i in range(2, 5):
            course = Course(i, f"课程{i}", f"学科{i}", EducationLevel.PRIMARY, TeachingMethod.LECTURE)
            record_id = education.enroll_course(course, current_time=0.0)
            education.update_learning_progress(record_id, 1.0, 30.0)
        
        # 检查教育水平
        assert education.education_level == EducationLevel.SECONDARY
    
    def test_education_summary(self):
        """测试教育摘要"""
        education = EducationComponent()
        
        # 添加一些数据
        education.add_knowledge("数学", 0.5)
        education.add_skill("计算", 0.3)
        education.is_teacher = True
        education.teaching_subjects = ["数学"]
        
        # 获取教育摘要
        summary = education.get_education_summary()
        
        # 检查摘要
        assert summary['education_level'] == 'ILLITERATE'
        assert '数学' in summary['subjects_studied']
        assert summary['total_knowledge_subjects'] == 1
        assert summary['total_skills'] == 1
        assert summary['is_teacher'] == True
        assert '数学' in summary['teaching_subjects']


class TestPhase3Integration:
    """Phase 3集成测试"""
    
    def test_disease_education_integration(self):
        """测试疾病和教育系统集成"""
        # 创建世界
        world = World()
        
        # 创建实体
        entity = world.create_entity()
        
        # 添加组件
        world.add_component(entity, HumanComponent())
        world.add_component(entity, SpaceComponent(x=0, y=0))
        world.add_component(entity, HealthComponent())
        world.add_component(entity, DiseaseManagerComponent())
        world.add_component(entity, EducationComponent())
        world.add_component(entity, CognitiveComponent())
        
        # 获取组件
        disease = world.get_component(entity, DiseaseManagerComponent)
        education = world.get_component(entity, EducationComponent)
        health = world.get_component(entity, HealthComponent)
        
        # 测试疾病影响教育
        disease_id = disease.add_disease("流感", DiseaseSeverity.MODERATE, TransmissionMode.AIRBORNE)
        
        # 检查疾病是否被正确添加
        assert disease_id in disease.current_diseases
        assert disease.current_diseases[disease_id].disease_type == "流感"
        
        # 检查感染概率
        infection_prob = disease.get_infection_probability("流感")
        assert 0.0 <= infection_prob <= 1.0
        
        # 测试教育能力
        education.add_knowledge("医学", 0.6)
        education.is_teacher = True
        education.teaching_subjects = ["医学"]
        
        # 检查教学能力
        assert education.can_teach("医学")
        effectiveness = education.get_teaching_effectiveness(LearningStyle.VISUAL)
        assert effectiveness > 0.0
    
    def test_social_disease_interaction(self):
        """测试社会和疾病交互"""
        # 创建世界
        world = World()
        
        # 创建两个实体
        entity1 = world.create_entity()
        entity2 = world.create_entity()
        
        # 添加组件
        for entity in [entity1, entity2]:
            world.add_component(entity, HumanComponent())
            world.add_component(entity, SpaceComponent(x=0, y=0))
            world.add_component(entity, DiseaseManagerComponent())
        
        # 获取组件
        disease1 = world.get_component(entity1, DiseaseManagerComponent)
        disease2 = world.get_component(entity2, DiseaseManagerComponent)
        
        # 实体1感染疾病
        disease1.add_disease("流感", DiseaseSeverity.MODERATE, TransmissionMode.AIRBORNE)
        
        # 检查实体2是否可能被感染
        infection_prob = disease2.get_infection_probability("流感")
        assert 0.0 <= infection_prob <= 1.0
        
        # 给实体2添加免疫力
        disease2.immunities["流感"] = 10.0
        
        # 检查免疫后感染概率
        assert disease2.get_infection_probability("流感") == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
