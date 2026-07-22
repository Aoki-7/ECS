#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
人类技术技能组件 v4.16.0
记录个体掌握的技术能力，技术由人类主观能动性驱动产生
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum, auto

from core.component import Component


class SkillProficiency(Enum):
    """技能熟练度等级"""
    NOVICE = auto()      # 初学
    APPRENTICE = auto() # 学徒
    JOURNEYMAN = auto() # 熟练
    EXPERT = auto()      # 专家
    MASTER = auto()      # 大师


@dataclass(slots=True)
class HumanTechSkillComponent(Component):
    """
    人类技术技能组件
    每个个体拥有独立的技术技能集，体现人类的主观能动性

    属性:
        skills: {技能名: {experience, proficiency, mastery_time}} 掌握的技能
        creativity: 创造力基础值 0-1，影响创新成功率
        research_focus: 当前主动研究的技能方向（可选）
        known_techniques: 已知的生产技术名列表（可用于教学传播）
        innovation_count: 个人创新次数（原创技术数量）
        total_practice_hours: 总实践时长（小时）
    """
    
    skills: Dict[str, Dict] = field(default_factory=dict)
    creativity: float = 0.3  # 基础创造力
    research_focus: str = ""  # 当前研究方向
    known_techniques: List[str] = field(default_factory=list)  # 已知的可生产技术
    innovation_count: int = 0  # 个人创新次数
    total_practice_hours: Dict[str, float] = field(default_factory=dict)  # 各领域实践时长
    
    def add_practice(self, domain: str, hours: float = 1.0) -> None:
        """增加某领域的实践时长"""
        self.total_practice_hours[domain] = self.total_practice_hours.get(domain, 0.0) + hours
    
    def get_practice_hours(self, domain: str) -> float:
        """获取某领域的实践时长"""
        return self.total_practice_hours.get(domain, 0.0)
    
    def has_skill(self, skill_name: str) -> bool:
        """检查是否掌握某技能"""
        return skill_name in self.skills
    
    def get_skill_level(self, skill_name: str) -> float:
        """获取技能熟练度数值 0-1"""
        if skill_name not in self.skills:
            return 0.0
        proficiency_values = {
            SkillProficiency.NOVICE: 0.2,
            SkillProficiency.APPRENTICE: 0.4,
            SkillProficiency.JOURNEYMAN: 0.6,
            SkillProficiency.EXPERT: 0.8,
            SkillProficiency.MASTER: 1.0,
        }
        skill = self.skills[skill_name]
        base = proficiency_values.get(skill.get('proficiency'), 0.1)
        experience_factor = min(1.0, skill.get('experience', 0) / 1000)
        return base + (1 - base) * experience_factor * 0.5
    
    def gain_experience(self, skill_name: str, exp: float, domain: str = "general") -> None:
        """增加技能经验，可能提升熟练度"""
        if skill_name not in self.skills:
            self.skills[skill_name] = {
                'experience': 0.0,
                'proficiency': SkillProficiency.NOVICE,
                'mastery_time': 0.0,
                'domain': domain,
                'created_by_self': False,
            }
        
        skill = self.skills[skill_name]
        skill['experience'] += exp
        
        # 根据经验升级熟练度
        exp_val = skill['experience']
        if exp_val >= 5000:
            skill['proficiency'] = SkillProficiency.MASTER
        elif exp_val >= 2000:
            skill['proficiency'] = SkillProficiency.EXPERT
        elif exp_val >= 800:
            skill['proficiency'] = SkillProficiency.JOURNEYMAN
        elif exp_val >= 300:
            skill['proficiency'] = SkillProficiency.APPRENTICE
    
    def create_skill(self, skill_name: str, domain: str, invention_time: float = 0.0) -> None:
        """
        创建一项新技能（原创技术）
        这代表人类个体通过主观能动性产生了新的技术掌握
        """
        if skill_name not in self.skills:
            self.skills[skill_name] = {
                'experience': 100.0,  # 初始有一些经验
                'proficiency': SkillProficiency.APPRENTICE,
                'mastery_time': invention_time,
                'domain': domain,
                'created_by_self': True,
            }
            self.innovation_count += 1
            self.known_techniques.append(skill_name)
    
    def learn_from_teacher(self, skill_name: str, teacher_level: float, domain: str = "general") -> None:
        """从他人那里学习技能（社会传播）"""
        if skill_name not in self.skills:
            self.skills[skill_name] = {
                'experience': 0.0,
                'proficiency': SkillProficiency.NOVICE,
                'mastery_time': 0.0,
                'domain': domain,
                'created_by_self': False,
            }
        
        # 学习效率取决于老师水平
        learn_amount = 20.0 * (0.5 + teacher_level * 0.5)
        self.gain_experience(skill_name, learn_amount, domain)
    
    def set_research_focus(self, focus: str, domain: str = "") -> None:
        """设置主动研究方向，体现主观能动性"""
        self.research_focus = focus
    
    def get_top_skills(self, n: int = 3) -> List[str]:
        """获取最熟练的n个技能"""
        sorted_skills = sorted(
            self.skills.items(),
            key=lambda x: x[1].get('experience', 0),
            reverse=True
        )
        return [name for name, _ in sorted_skills[:n]]
