#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:education_system.py
@说明:教育系统 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

import logging
import random
from typing import Dict, List, Optional, Set
from core.system import System
from core.world import World
from human.components.cognitive.education_component_v4 import EducationComponent, Course, Teacher, EducationLevel, TeachingMethod, LearningStyle
from human.components.cognitive.cognitive_component_v4 import CognitiveComponent
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from human.components.social.social_component_v4 import SocialManagerComponent, RelationshipType

logger = logging.getLogger(__name__)


class EducationSystem(System):
    """教育系统 v4.0 - 细化版"""
    tick_interval = 10  # 每10帧更新一次

    def __init__(self):
        self.learning_probability = 0.1      # 学习概率
        self.teaching_probability = 0.05     # 教学概率
        self.course_creation_probability = 0.02  # 课程创建概率
        
        # 课程库
        self.available_courses = {
            "基础数学": {
                "subject": "数学",
                "level": EducationLevel.PRIMARY,
                "teaching_method": TeachingMethod.LECTURE,
                "duration": 30.0,
                "difficulty": 0.3,
                "knowledge_gain": 0.2,
                "skill_gain": 0.1
            },
            "农业技术": {
                "subject": "农业",
                "level": EducationLevel.PRIMARY,
                "teaching_method": TeachingMethod.PRACTICE,
                "duration": 45.0,
                "difficulty": 0.4,
                "knowledge_gain": 0.3,
                "skill_gain": 0.4
            },
            "工艺制作": {
                "subject": "工艺",
                "level": EducationLevel.SECONDARY,
                "teaching_method": TeachingMethod.DEMONSTRATION,
                "duration": 60.0,
                "difficulty": 0.6,
                "knowledge_gain": 0.4,
                "skill_gain": 0.5
            },
            "医药知识": {
                "subject": "医药",
                "level": EducationLevel.HIGHER,
                "teaching_method": TeachingMethod.LECTURE,
                "duration": 90.0,
                "difficulty": 0.8,
                "knowledge_gain": 0.6,
                "skill_gain": 0.3
            }
        }

    def update(self, world: World, dt: float):
        """更新教育系统"""
        current_time = world.get_time().total_hours if world.get_time() else 0.0
        
        # 获取所有人类实体
        humans = []
        for e, (education, cognitive, human, pos) in world.get_components(
            EducationComponent, CognitiveComponent, HumanComponent, SpaceComponent
        ):
            humans.append((e.id, education, cognitive, pos))
        
        # 处理学习
        self._handle_learning(world, humans, current_time, dt)
        
        # 处理教学
        self._handle_teaching(world, humans, current_time)
        
        # 处理课程创建
        self._handle_course_creation(world, humans, current_time)
        
        # 更新教育水平
        self._update_education_levels(humans)

    def _handle_learning(self, world: World, humans: List, current_time: float, dt: float):
        """处理学习"""
        for entity_id, education, cognitive, pos in humans:
            # 随机学习
            if random.random() < self.learning_probability:
                # 如果当前没有学习课程，尝试注册新课程
                if education.current_course_id is None:
                    self._enroll_in_course(education, cognitive, current_time)
                
                # 如果有当前课程，更新学习进度
                elif education.current_course_id is not None:
                    self._update_learning_progress(education, cognitive, current_time, dt)

    def _enroll_in_course(self, education: EducationComponent, cognitive: CognitiveComponent, 
                         current_time: float):
        """注册课程"""
        # 根据教育水平和学习能力选择课程
        suitable_courses = []
        
        for course_name, course_info in self.available_courses.items():
            # 检查教育水平要求
            if self._is_suitable_level(education.education_level, course_info["level"]):
                suitable_courses.append(course_name)
        
        if suitable_courses:
            # 随机选择课程
            course_name = random.choice(suitable_courses)
            course_info = self.available_courses[course_name]
            
            # 创建课程对象
            course = Course(
                course_id=hash(course_name) % 10000,  # 简化ID生成
                name=course_name,
                subject=course_info["subject"],
                level=course_info["level"],
                teaching_method=course_info["teaching_method"],
                duration=course_info["duration"],
                difficulty=course_info["difficulty"],
                knowledge_gain=course_info["knowledge_gain"],
                skill_gain=course_info["skill_gain"]
            )
            
            # 注册课程
            record_id = education.enroll_course(course, current_time=current_time)
            logger.debug(f"[Education] 实体注册课程: {course_name}")

    def _update_learning_progress(self, education: EducationComponent, cognitive: CognitiveComponent, 
                                current_time: float, dt: float):
        """更新学习进度"""
        # 查找当前学习记录
        current_record = None
        for record in education.learning_records.values():
            if record.course_id == education.current_course_id and not record.is_completed():
                current_record = record
                break
        
        if current_record:
            # 计算学习进度增量
            base_progress = dt / 30.0  # 假设30天完成课程
            
            # 根据学习能力和智力调整进度
            ability_factor = (education.learning_ability + education.intelligence) / 2.0
            progress_delta = base_progress * ability_factor
            
            # 根据认知状态调整进度
            if hasattr(cognitive, 'focus_ability'):
                progress_delta *= cognitive.focus_ability
            
            # 更新进度
            education.update_learning_progress(current_record.record_id, progress_delta, current_time)
            
            # 添加知识和技能
            course_info = self.available_courses.get(
                next(name for name, info in self.available_courses.items() 
                     if hash(name) % 10000 == current_record.course_id),
                {"subject": "通用", "knowledge_gain": 0.1, "skill_gain": 0.1}
            )
            
            education.add_knowledge(course_info["subject"], course_info["knowledge_gain"] * progress_delta)
            education.add_skill(course_info["subject"], course_info["skill_gain"] * progress_delta)

    def _handle_teaching(self, world: World, humans: List, current_time: float):
        """处理教学"""
        # 查找潜在的教师和学生
        teachers = []
        students = []
        
        for entity_id, education, cognitive, pos in humans:
            if education.is_teacher:
                teachers.append((entity_id, education, pos))
            elif education.current_course_id is not None:
                students.append((entity_id, education, pos))
        
        # 为每个学生寻找合适的教师
        for student_id, student_education, student_pos in students:
            # 查找附近的教师
            nearby_teachers = self._find_nearby_teachers(world, student_pos, teachers, radius=15.0)
            
            if nearby_teachers:
                # 选择最合适的教师
                best_teacher = self._select_best_teacher(nearby_teachers, student_education)
                
                if best_teacher:
                    teacher_id, teacher_education, _ = best_teacher
                    
                    # 建立师生关系
                    self._establish_teaching_relationship(world, student_id, teacher_id, current_time)
                    
                    # 更新学习记录的教师信息
                    for record in student_education.learning_records.values():
                        if record.course_id == student_education.current_course_id and not record.is_completed():
                            record.teacher_id = teacher_id
                            break

    def _find_nearby_teachers(self, world: World, pos: SpaceComponent, teachers: List, radius: float) -> List:
        """查找附近的教师"""
        nearby_teachers = []
        
        for teacher_id, teacher_education, teacher_pos in teachers:
            distance = ((pos.x - teacher_pos.x)**2 + (pos.y - teacher_pos.y)**2)**0.5
            if distance <= radius:
                nearby_teachers.append((teacher_id, teacher_education, teacher_pos))
        
        return nearby_teachers

    def _select_best_teacher(self, teachers: List, student_education: EducationComponent) -> Optional[tuple]:
        """选择最佳教师"""
        best_teacher = None
        best_effectiveness = 0.0
        
        for teacher_id, teacher_education, teacher_pos in teachers:
            # 检查教师是否能教授当前课程
            if student_education.current_course_id:
                # 简化实现：检查教师是否教授相关学科
                can_teach = any(subject in teacher_education.teaching_subjects 
                              for subject in student_education.subjects_studied)
                
                if can_teach:
                    # 计算教学有效性
                    effectiveness = teacher_education.get_teaching_effectiveness(student_education.learning_style)
                    
                    if effectiveness > best_effectiveness:
                        best_effectiveness = effectiveness
                        best_teacher = (teacher_id, teacher_education, teacher_pos)
        
        return best_teacher

    def _establish_teaching_relationship(self, world: World, student_id: int, teacher_id: int, current_time: float):
        """建立师生关系"""
        # 获取社会组件
        student_entity = world.query_entity(student_id)
        teacher_entity = world.query_entity(teacher_id)
        
        if student_entity and teacher_entity:
            student_social = world.get_component(student_entity, SocialManagerComponent)
            teacher_social = world.get_component(teacher_entity, SocialManagerComponent)
            
            if student_social and teacher_social:
                # 添加师生关系
                student_social.add_relationship(teacher_id, RelationshipType.MENTOR, strength=0.6)
                teacher_social.add_relationship(student_id, RelationshipType.STUDENT, strength=0.6)
                
                logger.debug(f"[Education] 建立师生关系: 学生{student_id} - 教师{teacher_id}")

    def _handle_course_creation(self, world: World, humans: List, current_time: float):
        """处理课程创建"""
        # 查找有教学能力的实体
        potential_teachers = []
        
        for entity_id, education, cognitive, pos in humans:
            if (education.education_level in [EducationLevel.HIGHER, EducationLevel.EXPERT] and 
                not education.is_teacher and 
                random.random() < self.course_creation_probability):
                potential_teachers.append((entity_id, education, cognitive))
        
        # 使一些实体成为教师
        for entity_id, education, cognitive in potential_teachers:
            # 设置为教师
            education.is_teacher = True
            
            # 根据知识和技能确定可教授学科
            teaching_subjects = []
            for subject, knowledge_level in education.knowledge.items():
                if knowledge_level > 0.6:  # 知识水平足够高才能教授
                    teaching_subjects.append(subject)
            
            education.teaching_subjects = teaching_subjects
            education.teaching_ability = (education.intelligence + cognitive.problem_solving_ability) / 2.0
            
            logger.info(f"[Education] 实体{entity_id}成为教师，可教授学科: {teaching_subjects}")

    def _update_education_levels(self, humans: List):
        """更新教育水平"""
        for entity_id, education, cognitive, pos in humans:
            # 教育水平已经在complete_course中更新
            pass

    def _is_suitable_level(self, current_level: EducationLevel, course_level: EducationLevel) -> bool:
        """检查是否适合课程水平"""
        level_order = {
            EducationLevel.ILLITERATE: 0,
            EducationLevel.PRIMARY: 1,
            EducationLevel.SECONDARY: 2,
            EducationLevel.HIGHER: 3,
            EducationLevel.EXPERT: 4
        }
        
        current_order = level_order.get(current_level, 0)
        course_order = level_order.get(course_level, 0)
        
        # 可以学习同级或低一级的课程
        return course_order <= current_order + 1

    def get_education_statistics(self, world: World) -> Dict:
        """获取教育统计"""
        total_entities = 0
        teachers_count = 0
        students_count = 0
        education_level_counts = {}
        subject_popularity = {}
        
        for e, (education, human) in world.get_components(EducationComponent, HumanComponent):
            total_entities += 1
            
            if education.is_teacher:
                teachers_count += 1
            
            if education.current_course_id is not None:
                students_count += 1
            
            # 统计教育水平
            level = education.education_level.name
            education_level_counts[level] = education_level_counts.get(level, 0) + 1
            
            # 统计学科受欢迎程度
            for subject in education.subjects_studied:
                subject_popularity[subject] = subject_popularity.get(subject, 0) + 1
        
        return {
            'total_entities': total_entities,
            'teachers_count': teachers_count,
            'students_count': students_count,
            'teacher_student_ratio': teachers_count / students_count if students_count > 0 else 0.0,
            'education_level_distribution': education_level_counts,
            'subject_popularity': subject_popularity
        }
