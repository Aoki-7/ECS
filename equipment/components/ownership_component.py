#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:ownership_component.py
@说明:物品所属权组件
@时间:2026/04/13
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass
from typing import Optional

from core.component import Component
from core.entity import Entity


@dataclass
class OwnershipComponent(Component):
    """
    物品所属权组件
    
    用来表示物品的所有者身份。物品被拾取后，仍然存在于世界中，
    但通过此组件标记其所有者，使其对其他实体不可见。
    
    Attributes:
        owner_id: 所有者的实体ID（None表示无主状态）
        visibility: 可见性范围
                   - "none": 仅所有者可见
                   - "group": 所有者及其组织可见
                   - "public": 所有人可见
    """
    
    owner_id: Optional[int] = None  # 所有者实体ID
    visibility: str = "none"         # 可见性级别
    
    def is_owned(self) -> bool:
        """检查物品是否被所有"""
        return self.owner_id is not None
    
    def set_owner(self, owner_entity: Entity) -> None:
        """设置所有者"""
        self.owner_id = owner_entity.id
        self.visibility = "none"
    
    def release_ownership(self) -> None:
        """释放所有权"""
        self.owner_id = None
        self.visibility = "public"
    
    def check_visible_to(self, observer_id: int) -> bool:
        """检查是否对观察者可见"""
        if self.visibility == "public":
            return True
        if self.visibility == "none":
            return self.owner_id == observer_id
        # "group" 情况需要组织系统支持，暂时简化处理
        return self.owner_id == observer_id
