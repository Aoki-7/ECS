#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:social_component.py
@说明:社会关系组件
@时间:2026/03/13 11:21:48
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component


@dataclass
class SocialComponent(Component):
    """
    社会关系组件
    
    用于管理实体与其他实体的社会关系、家庭关系和友谊。
    
    属性:
        relations: 关系映射表 {entity_id: relation_score}，关系值范围 -100 到 100
        family: 家庭成员ID列表
        friends: 朋友ID列表
        acquaintances: 熟人ID列表
    """
    relations: Dict[int, float] = field(default_factory=dict)  # entity_id -> relation_score (-100 ~ 100)
    family: List[int] = field(default_factory=list)  # 家庭成员ID
    friends: List[int] = field(default_factory=list)  # 朋友ID
    acquaintances: List[int] = field(default_factory=list)  # 熟人ID
    
    def add_relation(self, entity_id: int, score: float = 0.0) -> None:
        """添加关系"""
        self.relations[entity_id] = max(-100, min(100, score))
    
    def update_relation(self, entity_id: int, delta: float) -> None:
        """修改关系分值"""
        if entity_id in self.relations:
            self.relations[entity_id] = max(-100, min(100, self.relations[entity_id] + delta))
        else:
            self.add_relation(entity_id, delta)
    
    def get_relation(self, entity_id: int) -> float:
        """获取关系分值"""
        return self.relations.get(entity_id, 0.0)
    
    def is_family(self, entity_id: int) -> bool:
        """检查是否为家庭成员"""
        return entity_id in self.family
    
    def is_friend(self, entity_id: int) -> bool:
        """检查是否为朋友"""
        return entity_id in self.friends
    
    def is_acquaintance(self, entity_id: int) -> bool:
        """检查是否为熟人"""
        return entity_id in self.acquaintances