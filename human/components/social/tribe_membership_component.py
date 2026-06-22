#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:tribe_membership_component.py
@说明:部落成员组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component

@dataclass(slots=True)
class TribeMembershipComponent(Component):
    """
    部落成员组件 - 纯数据版
    存储部落成员信息。
    """
    # 所属部落
    tribe_id: Optional[int] = None
    
    # 在部落中的角色
    role: str = "member"
    
    # 忠诚度
    loyalty: float = 0.5
    
    # 贡献度
    contribution: float = 0.0
    
    # 加入时间
    joined_tick: int = 0
    
    # 状态
    is_active_member: bool = True

    # 兼容旧系统：add_loyalty 方法
    def add_loyalty(self, amount: float) -> None:
        """增加忠诚度"""
        self.loyalty = min(1.0, max(0.0, self.loyalty + amount))

    def is_member(self) -> bool:
        """是否为活跃成员"""
        return self.tribe_id is not None and self.is_active_member
