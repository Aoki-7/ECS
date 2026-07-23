#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:education_component.py
@说明:教育组件 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum, auto

from core.component import Component


class EducationLevel(Enum):
    """教育水平"""
    ILLITERATE = auto()     # 文盲
    PRIMARY = auto()        # 小学
    SECONDARY = auto()      # 中学
    HIGHER = auto()         # 高等教育
    EXPERT = auto()         # 专家


class TeachingMethod(Enum):
    """教学方法"""
    LECTURE = auto()        # 讲授
    DEMONSTRATION = auto()  # 演示
    PRACTICE = auto()       # 实践
    DISCUSSION = auto()     # 讨论
    SELF_STUDY = auto()     # 自学
    APPRENTICESHIP = auto() # 学徒制


class LearningStyle(Enum):
    """学习风格"""
    VISUAL = auto()         # 视觉学习
    AUDITORY = auto()       # 听觉学习
    KINESTHETIC = auto()    # 动觉学习
    READING = auto()        # 阅读学习
    SOCIAL = auto()         # 社交学习
    SOLITARY = auto()       # 独立学习


@dataclass(slots=True)
class Course:
    """课程"""
    course_id: int
    name: str
    subject: str                    # 学科（如"数学"、"农业"、"工艺"）
    level: EducationLevel           # 课程水平
    teaching_method: TeachingMethod # 教学方法
    
    # 课程属性
    duration: float = 30.0          # 课程时长（天）
    difficulty: float = 0.5         # 难度 (0-1)
    prerequisites: List[str] = field(default_factory=list)  # 先修课程
    
    # 学习效果
    knowledge_gain: float = 0.3     # 知识增益
    skill_gain: float = 0.2         # 技能增益
    
    # 状态
    enrolled_students: Set[int] = field(default_factory=set)  # 注册学生
    completed_students: Set[int] = field(default_factory=set)  # 完成学生
    
    def is_completed_by(self, student_id: int) -> bool:
        """是否被学生完成"""
        return student_id in self.completed_students


@dataclass(slots=True)
class Teacher:
    """教师"""
    teacher_id: int
    name: str
    subjects: List[str]             # 教授学科
    teaching_ability: float = 0.7   # 教学能力 (0-1)
    experience: float = 0.5         # 教学经验 (0-1)
    
    # 教学风格
    preferred_methods: List[TeachingMethod] = field(default_factory=list)
    patience: float = 0.6           # 耐心 (0-1)
    strictness: float = 0.5         # 严格程度 (0-1)
    
    # 学生管理
    current_students: Set[int] = field(default_factory=set)  # 当前学生
    max_students: int = 10          # 最大学生数
    
    def can_teach_more_students(self) -> bool:
        """是否能教更多学生"""
        return len(self.current_students) < self.max_students
    
    def get_teaching_effectiveness(self, student_learning_style: LearningStyle) -> float:
        """获取教学有效性"""
        base_effectiveness = self.teaching_ability * self.experience
        
        # 根据教学风格调整有效性
        style_bonus = 0.0
        if student_learning_style == LearningStyle.VISUAL and TeachingMethod.DEMONSTRATION in self.preferred_methods:
            style_bonus = 0.2
        elif student_learning_style == LearningStyle.KINESTHETIC and TeachingMethod.PRACTICE in self.preferred_methods:
            style_bonus = 0.2
        elif student_learning_style == LearningStyle.SOCIAL and TeachingMethod.DISCUSSION in self.preferred_methods:
            style_bonus = 0.2
        
        return min(1.0, base_effectiveness + style_bonus)


@dataclass(slots=True)
class LearningRecord:
    """学习记录"""
    record_id: int
    student_id: int
    course_id: int
    teacher_id: Optional[int]
    
    # 学习进度
    start_time: float
    completion_time: Optional[float] = None
    progress: float = 0.0           # 进度 (0-1)
    
    # 学习成果
    knowledge_gained: float = 0.0
    skill_gained: float = 0.0
    final_score: float = 0.0        # 最终成绩 (0-1)
    
    # 学习过程
    attendance_rate: float = 1.0    # 出勤率 (0-1)
    participation: float = 0.5      # 参与度 (0-1)
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.completion_time is not None
    
    def get_duration(self) -> float:
        """获取学习时长"""
        if self.completion_time is None:
            return 0.0
        return self.completion_time - self.start_time


@dataclass(slots=True)
class EducationComponent(Component):
    """
    教育组件 v4.0 - 细化版
    包括教育水平、学习记录、教学能力等细化功能。
    """
    
    # === 教育水平 ===
    education_level: EducationLevel = EducationLevel.ILLITERATE  # 当前教育水平
    subjects_studied: Set[str] = field(default_factory=set)  # 已学习学科
    
    # === 学习能力 ===
    learning_style: LearningStyle = LearningStyle.VISUAL  # 学习风格
    learning_ability: float = 0.5   # 学习能力 (0-1)
    intelligence: float = 0.5       # 智力 (0-1)
    
    # === 学习记录 ===
    learning_records: Dict[int, LearningRecord] = field(default_factory=dict)  # 记录ID -> 学习记录
    next_record_id: int = 0
    current_course_id: Optional[int] = None  # 当前学习课程
    
    # === 知识和技能 ===
    knowledge: Dict[str, float] = field(default_factory=dict)  # 学科 -> 知识水平 (0-1)
    skills: Dict[str, float] = field(default_factory=dict)     # 技能 -> 技能水平 (0-1)
    
    # === 教学能力（如果是教师）===
    is_teacher: bool = False
    teaching_subjects: List[str] = field(default_factory=list)  # 可教授学科
    teaching_ability: float = 0.5   # 教学能力 (0-1)
    
    # === 教育历史 ===
    education_history: List[Dict] = field(default_factory=list)  # 教育历史
    max_history_length: int = 50
    
    def enroll_course(self, course: Course, teacher_id: Optional[int] = None, 
                     current_time: float = 0.0) -> int:
        """注册课程"""
        record_id = self.next_record_id
        self.next_record_id += 1
        
        record = LearningRecord(
            record_id=record_id,
            student_id=0,  # 实际应用中应该使用真实学生ID
            course_id=course.course_id,
            teacher_id=teacher_id,
            start_time=current_time
        )
        
        self.learning_records[record_id] = record
        self.current_course_id = course.course_id
        
        return record_id
    
    def update_learning_progress(self, record_id: int, progress_delta: float, 
                                current_time: float):
        """更新学习进度"""
        if record_id not in self.learning_records:
            return
        
        record = self.learning_records[record_id]
        record.progress = min(1.0, record.progress + progress_delta)
        
        # 如果完成课程
        if record.progress >= 1.0 and record.completion_time is None:
            record.completion_time = current_time
            self.complete_course(record_id, current_time)
    
    def complete_course(self, record_id: int, current_time: float):
        """完成课程"""
        if record_id not in self.learning_records:
            return
        
        record = self.learning_records[record_id]
        
        # 记录到教育历史
        self.education_history.append({
            'course_id': record.course_id,
            'completion_time': current_time,
            'duration': record.get_duration(),
            'final_score': record.final_score,
            'knowledge_gained': record.knowledge_gained,
            'skill_gained': record.skill_gained
        })
        
        # 限制历史记录长度
        if len(self.education_history) > self.max_history_length:
            self.education_history = self.education_history[-self.max_history_length:]
        
        # 更新教育水平
        self._update_education_level()
    
    def _update_education_level(self):
        """更新教育水平"""
        completed_courses = [r for r in self.learning_records.values() if r.is_completed()]
        
        if len(completed_courses) >= 10:
            self.education_level = EducationLevel.EXPERT
        elif len(completed_courses) >= 7:
            self.education_level = EducationLevel.HIGHER
        elif len(completed_courses) >= 4:
            self.education_level = EducationLevel.SECONDARY
        elif len(completed_courses) >= 1:
            self.education_level = EducationLevel.PRIMARY
        else:
            self.education_level = EducationLevel.ILLITERATE
    
    def add_knowledge(self, subject: str, amount: float):
        """添加知识"""
        if subject not in self.knowledge:
            self.knowledge[subject] = 0.0
        
        self.knowledge[subject] = min(1.0, self.knowledge[subject] + amount)
        self.subjects_studied.add(subject)
    
    def add_skill(self, skill: str, amount: float):
        """添加技能"""
        if skill not in self.skills:
            self.skills[skill] = 0.0
        
        self.skills[skill] = min(1.0, self.skills[skill] + amount)
    
    def get_knowledge_level(self, subject: str) -> float:
        """获取知识水平"""
        return self.knowledge.get(subject, 0.0)
    
    def get_skill_level(self, skill: str) -> float:
        """获取技能水平"""
        return self.skills.get(skill, 0.0)
    
    def can_teach(self, subject: str) -> bool:
        """是否能教授学科"""
        return self.is_teacher and subject in self.teaching_subjects
    
    def get_teaching_effectiveness(self, student_learning_style: LearningStyle) -> float:
        """获取教学有效性"""
        if not self.is_teacher:
            return 0.0
        
        base_effectiveness = self.teaching_ability * self.intelligence
        
        # 根据学习风格调整有效性
        style_bonus = 0.0
        if student_learning_style == LearningStyle.VISUAL and "demonstration" in self.teaching_subjects:
            style_bonus = 0.1
        elif student_learning_style == LearningStyle.KINESTHETIC and "practice" in self.teaching_subjects:
            style_bonus = 0.1
        
        return min(1.0, base_effectiveness + style_bonus)
    
    def get_education_summary(self) -> Dict:
        """获取教育摘要"""
        return {
            'education_level': self.education_level.name,
            'subjects_studied': list(self.subjects_studied),
            'current_course_id': self.current_course_id,
            'completed_courses': len([r for r in self.learning_records.values() if r.is_completed()]),
            'total_knowledge_subjects': len(self.knowledge),
            'total_skills': len(self.skills),
            'is_teacher': self.is_teacher,
            'teaching_subjects': self.teaching_subjects
        }