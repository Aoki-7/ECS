#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:role_component.py
@说明:角色相关组件（纯数据）
@时间:2026/04/27
@版本:2.0

业务逻辑已迁移至 human/systems/social/role_system.py
'''

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum, auto

from core.component import Component


class RoleType(Enum):
    """角色类型枚举"""
    FAMILY = auto()
    OCCUPATION = auto()
    COMMUNITY = auto()
    SOCIAL = auto()
    RELATIONAL = auto()


@dataclass
class Role:
    """角色数据结构"""
    title: str
    description: str
    responsibility_list: List[str]
    importance: float = 50.0

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "description": self.description,
            "responsibilities": self.responsibility_list,
            "importance": self.importance
        }


@dataclass(slots=True)
class RoleComponent(Component):
    """
    角色组件 — 纯数据容器

    在群体中承担的角色列表，按类型分组。
    所有业务逻辑由 RoleSystem 管理。
    """
    _roles: Dict[RoleType, List[Role]] = field(default_factory=lambda: {
        RoleType.FAMILY: [],
        RoleType.OCCUPATION: [],
        RoleType.COMMUNITY: [],
        RoleType.SOCIAL: [],
        RoleType.RELATIONAL: []
    })


@dataclass(slots=True)
class IdentityShiftComponent(Component):
    """
    身份转换组件 — 纯数据容器

    情境身份切换的公开/私下面具。
    切换逻辑由 RoleSystem 管理。
    """
    public_identity: str = ""
    private_identity: str = ""


@dataclass(slots=True)
class ResponsibilityComponent(Component):
    """
    责任组件 — 纯数据容器

    角色责任的详细追踪。
    履行/违反记录逻辑由 RoleSystem 管理。
    """
    role_owner: int = 0
    role_title: str = ""
    responsibilities: List[str] = field(default_factory=list)
    fulfilled: Dict[str, bool] = field(default_factory=dict)
    violation_history: List[Dict] = field(default_factory=list)