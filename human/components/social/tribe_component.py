#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:tribe_component.py
@说明:部落组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component

@dataclass(slots=True)
class TribeComponent(Component):
    """
    部落组件 - 纯数据版
    存储部落信息。
    """
    # 部落成员 {entity_id: role}
    members: Dict[int, str] = field(default_factory=dict)
    
    # 部落领袖
    leader_id: Optional[int] = None
    
    # 部落领土
    territory_center: Optional[tuple] = None
    territory_radius: float = 0.0
    
    # 部落属性
    tribe_name: str = ""
    tribe_size: int = 0
    max_size: int = 50
    
    # 部落状态
    is_active: bool = True
    founded_tick: int = 0

    @property
    def name(self) -> str:
        """兼容旧系统：name 属性映射到 tribe_name"""
        return self.tribe_name

    @name.setter
    def name(self, value: str) -> None:
        """兼容旧系统：name 属性映射到 tribe_name"""
        self.tribe_name = value

    def get_member_count(self) -> int:
        """获取成员数量"""
        return len(self.members)

    def add_member(self, entity_id: int, role: str = "member") -> None:
        """添加成员"""
        self.members[entity_id] = role
        self.tribe_size = len(self.members)

    def remove_member(self, entity_id: int) -> None:
        """移除成员"""
        if entity_id in self.members:
            del self.members[entity_id]
            self.tribe_size = len(self.members)

    @property
    def member_ids(self) -> List[int]:
        """获取成员 ID 列表"""
        return list(self.members.keys())

    @property
    def home_territory(self) -> tuple:
        """获取部落中心位置"""
        return self.territory_center if self.territory_center else (0.0, 0.0)

    @home_territory.setter
    def home_territory(self, value: tuple) -> None:
        """设置部落中心位置"""
        self.territory_center = value

    def set_leader(self, entity_id: int) -> None:
        """设置领袖"""
        self.leader_id = entity_id
