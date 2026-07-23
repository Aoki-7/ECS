#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
书籍组件 v4.16.0
用于存储和传播技术技能，实现技术的非生物传承
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from core.component import Component


@dataclass(slots=True)
class BookComponent(Component):
    """
    书籍/铭文/手册组件
    可以存储技术技能，人类可以通过阅读学习其中的知识
    实现技术脱离人类个体的传承，避免失传

    属性:
        title: 书籍标题
        author_id: 作者ID（人类实体ID）
        creation_time: 创作时间
        content_type: 内容类型（"tech_manual", "history", "literature"等）
        stored_skills: 存储的技能列表，每个技能包含名称、领域、经验值
        quality: 书籍品质 0-1，影响学习效率
        read_count: 被阅读次数
        durability: 耐久度 0-1，耐久为0则损坏无法阅读
        language: 语言类型，不同文明的语言需要破译才能阅读
    """
    
    title: str = "未知书籍"
    author_id: int = -1
    creation_time: float = 0.0
    content_type: str = "tech_manual"
    stored_skills: List[Dict] = field(default_factory=list)
    quality: float = 0.5
    read_count: int = 0
    durability: float = 1.0
    language: str = "common"
    
    def add_skill(self, skill_name: str, domain: str, experience_value: float = 100.0) -> None:
        """向书籍中添加一个技能"""
        self.stored_skills.append({
            'skill_name': skill_name,
            'domain': domain,
            'experience': experience_value
        })
    
    def get_learnable_skills(self) -> List[Dict]:
        """获取可学习的技能列表，损坏时返回空"""
        if self.durability <= 0:
            return []
        return self.stored_skills.copy()
    
    def read(self, reader_intelligence: float = 0.5) -> Optional[List[Dict]]:
        """
        阅读书籍，返回可学习的技能和可获得的经验
        品质越高、读者智商越高，获得的经验越多
        """
        if self.durability <= 0:
            return None
        
        self.read_count += 1
        # 每次阅读消耗耐久度，阅读次数越多越容易损坏
        self.durability -= 0.01 / self.quality
        
        learn_result = []
        learn_efficiency = 0.3 + self.quality * 0.4 + reader_intelligence * 0.3
        
        for skill in self.stored_skills:
            gained_exp = skill['experience'] * learn_efficiency
            learn_result.append({
                'skill_name': skill['skill_name'],
                'domain': skill['domain'],
                'experience': gained_exp
            })
        
        return learn_result
    
    def is_usable(self) -> bool:
        """检查书籍是否还能阅读"""
        return self.durability > 0