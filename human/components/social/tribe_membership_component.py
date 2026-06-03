#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:tribe_membership_component.py
@说明:部落成员身份组件
@时间:2026/05/23
@版本:1.0
'''

from dataclasses import dataclass
from typing import Optional

from core.component import Component


@dataclass(slots=True)
class TribeMembershipComponent(Component):
    """
    部落成员身份组件
    
    用于标记人类实体所属的部落及其在部落中的身份。
    
    属性:
        tribe_id: 所属部落实体ID（None表示无部落/游牧）
        role: 角色 (member, leader, elder)
        loyalty: 忠诚度 0-100
        joined_time: 加入时间（总小时）
        contribution: 对部落的贡献值
    """
    tribe_id: Optional[int] = None
    role: str = "member"        # member, leader, elder
    loyalty: float = 50.0       # 0-100
    joined_time: float = 0.0
    contribution: float = 0.0   # 贡献值（社交、繁衍、采集等累计）
    
    def is_member(self) -> bool:
        """是否属于某个部落"""
        return self.tribe_id is not None
    
    def is_leader(self) -> bool:
        """是否是领袖"""
        return self.role == "leader"
    
    def add_loyalty(self, delta: float) -> None:
        """增加/减少忠诚度"""
        self.loyalty = max(0.0, min(100.0, self.loyalty + delta))
    
    def add_contribution(self, delta: float) -> None:
        """增加贡献值"""
        self.contribution += delta
