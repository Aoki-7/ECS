#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:tribe_component.py
@说明:部落组件
@时间:2026/05/23
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

from core.component import Component


@dataclass
class TribeComponent(Component):
    """
    部落组件
    
    用于管理部落级别的信息，应挂载在独立的部落实体上。
    
    属性:
        name: 部落名称
        leader_id: 当前领袖的实体ID
        member_ids: 成员实体ID列表
        culture: 文化特征字典
        formed_time: 形成时间（总小时）
        home_territory: 领地中心 (x, y)
        territory_radius: 领地半径
    """
    name: str = "未命名部落"
    leader_id: Optional[int] = None
    member_ids: List[int] = field(default_factory=list)
    culture: Dict[str, float] = field(default_factory=lambda: {
        "cooperation": 0.5,      # 合作倾向
        "aggression": 0.3,       # 攻击性
        "tradition": 0.5,        # 传统保守度
        "openness": 0.5,         # 开放程度
    })
    formed_time: float = 0.0
    home_territory: Tuple[float, float] = field(default_factory=lambda: (50.0, 50.0))
    territory_radius: float = 20.0
    
    def add_member(self, entity_id: int) -> None:
        """添加成员"""
        if entity_id not in self.member_ids:
            self.member_ids.append(entity_id)
    
    def remove_member(self, entity_id: int) -> None:
        """移除成员"""
        if entity_id in self.member_ids:
            self.member_ids.remove(entity_id)
        if self.leader_id == entity_id:
            self.leader_id = None
    
    def set_leader(self, entity_id: int) -> None:
        """设置领袖"""
        if entity_id in self.member_ids:
            self.leader_id = entity_id
    
    def get_member_count(self) -> int:
        """获取成员数量"""
        return len(self.member_ids)
    
    def is_member(self, entity_id: int) -> bool:
        """检查是否为成员"""
        return entity_id in self.member_ids
    
    def update_territory(self, center_x: float, center_y: float) -> None:
        """更新领地中心"""
        self.home_territory = (center_x, center_y)
