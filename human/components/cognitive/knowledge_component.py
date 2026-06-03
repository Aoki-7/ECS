#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:knowledge_component.py
@说明:知识组件 - 存储实体的知识和技能
@时间:2026/04/18 10:00:00
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Set, Dict, Any
from core.component import Component


@dataclass(slots=True)
class KnowledgeComponent(Component):
    """
    知识组件

    存储实体的知识、技能和学习到的信息。
    包括：
    - 已知技术
    - 学习到的技能
    - 文化知识
    - 经验教训
    """

    # 已知技术集合
    known_technologies: Set[str] = field(default_factory=set)

    # 学习到的技能水平
    learned_skills: Dict[str, float] = field(default_factory=dict)

    # 文化知识
    cultural_knowledge: Dict[str, Any] = field(default_factory=dict)

    # 经验教训
    lessons_learned: Dict[str, Any] = field(default_factory=dict)

    def add_technology(self, technology: str):
        """添加已知技术"""
        self.known_technologies.add(technology)

    def has_technology(self, technology: str) -> bool:
        """检查是否知道某技术"""
        return technology in self.known_technologies

    def add_skill_knowledge(self, skill_name: str, level: float):
        """添加技能知识"""
        self.learned_skills[skill_name] = level

    def get_skill_knowledge(self, skill_name: str) -> float:
        """获取技能知识水平"""
        return self.learned_skills.get(skill_name, 0.0)

    def add_cultural_fact(self, key: str, value: Any):
        """添加文化事实"""
        self.cultural_knowledge[key] = value

    def get_cultural_fact(self, key: str) -> Any:
        """获取文化事实"""
        return self.cultural_knowledge.get(key)

    def add_lesson(self, lesson_key: str, lesson_data: Any):
        """添加经验教训"""
        self.lessons_learned[lesson_key] = lesson_data

    def get_lesson(self, lesson_key: str) -> Any:
        """获取经验教训"""
        return self.lessons_learned.get(lesson_key)