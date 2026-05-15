#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:role_component.py
@说明:角色组件 - 在群体中承担的角色
@时间:2026/04/27
@作者:Coder Agent
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum, auto

from core.component import Component


class RoleType(Enum):
    """角色类型枚举"""
    FAMILY = auto()      # 家庭角色
    OCCUPATION = auto()  # 职业角色
    COMMUNITY = auto()   # 社区角色
    SOCIAL = auto()      # 社交角色
    RELATIONAL = auto()  # 关系角色


@dataclass
class RoleComponent(Component):
    """
    角色组件 - 在群体中承担的角色
    
    特点：
    - 多重角色（一个人可以有多个角色）
    - 角色冲突（不同角色的期望可能冲突）
    - 角色转换（在不同情境下扮演不同角色）
    
    使用示例：
        role = RoleComponent()
        role.add_role(RoleType.FAMILY, "儿子", responsibilities=...)
        role.add_role(RoleType.OCCUPATION, "程序员", responsibilities=...)
    """
    
    def __init__(self):
        super().__init__()
        self._roles: Dict[RoleType, List['Role']] = {
            RoleType.FAMILY: [],
            RoleType.OCCUPATION: [],
            RoleType.COMMUNITY: [],
            RoleType.SOCIAL: [],
            RoleType.RELATIONAL: []
        }

    def add_role(self, role_type: RoleType, 
                 title: str, 
                 description: str = "",
                 responsibilities: List[str] = None,
                 importance: float = 50.0) -> 'Role':
        """
        添加角色
        
        Args:
            role_type: 角色类型
            title: 角色标题（如"儿子"、"程序员"）
            description: 角色描述
            responsibilities: 责任列表
            importance: 该角色的重要性权重 (0-100)
        
        Returns:
            创建的角色对象
        """
        role = Role(title=title, 
                    description=description,
                    responsibility_list=responsibilities or [],
                    importance=importance)
        
        self._roles[role_type].append(role)
        return role

    def get_primary_role(self, role_type: RoleType) -> Optional['Role']:
        """获取某类型的主要角色（重要性最高的）"""
        roles = self._roles[role_type]
        if not roles:
            return None
        return max(roles, key=lambda r: r.importance)

    def get_active_role(self, context: str) -> Optional['Role']:
        """根据情境获取当前活跃角色"""
        # 简单基于关键词匹配
        keywords = {
            "家庭": [RoleType.FAMILY],
            "工作": [RoleType.OCCUPATION],
            "社区": [RoleType.COMMUNITY],
            "朋友聚会": [RoleType.SOCIAL],
        }
        
        if any(kw in context for kw in keywords.get("家庭", [])):
            return self.get_primary_role(RoleType.FAMILY)
        elif any(kw in context for kw in keywords.get("工作", [])):
            return self.get_primary_role(RoleType.OCCUPATION)
        # ... 其他情境匹配
        
        return None

    def get_all_roles(self) -> List['Role']:
        """获取所有角色的扁平列表"""
        result = []
        for roles in self._roles.values():
            result.extend(roles)
        return result

    def has_conflict(self, role1: 'Role', role2: 'Role') -> bool:
        """检查两个角色是否存在责任冲突"""
        # 简单检查：如果责任描述有矛盾，认为存在冲突
        resp1 = role1.responsibility_list
        resp2 = role2.responsibility_list
        
        conflict_pairs = [("照顾家人", "加班工作"), 
                         ("遵守命令", "坚持原则")]
        
        for r1 in resp1:
            for r2 in resp2:
                if any((r1, r2) == pair for pair in conflict_pairs):
                    return True
        return False


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


@dataclass
class IdentityShiftComponent(Component):
    """
    身份转换组件 - 情境身份切换
    
    特点：
    - 在不同情境下呈现不同的自我
    - 角色面具（公开/私下表现不同）
    - 身份认同冲突的处理
    """
    
    def __init__(self, 
                 public_identity: str = "",
                 private_identity: str = ""):
        super().__init__()
        self._public = public_identity
        self._private = private_identity

    def switch(self, context: str) -> Dict:
        """根据情境切换身份显示"""
        # 简单实现：关键字判断
        if any(kw in context for kw in ["公众", "正式", "工作"]):
            return {"display": self._public}
        else:
            return {"display": self._private}

    def get_mask(self) -> str:
        """获取当前情境的身份面具"""
        return self._public if hasattr(self, '_public') and self._public else "default"


@dataclass
class ResponsibilityComponent(Component):
    """
    责任组件 - 角色责任的详细追踪
    
    用途：
    - 检查是否履行了角色责任
    - 记录责任违反情况
    - 提供道德判断依据
    """
    
    def __init__(self, 
                 role_owner: int,
                 role: str,
                 responsibilities: List[str] = None):
        super().__init__()
        
        self.role_owner = role_owner
        self._role = role
        self._responsibilities = responsibilities or []
        self._fulfilled: Dict[str, bool] = {}
        self._violation_history: List[Dict] = []

    def record_fulfillment(self, responsibility: str) -> None:
        """记录责任履行"""
        if responsibility in self._responsibilities:
            self._fulfilled[responsibility] = True

    def record_violation(self, responsibility: str, severity: float = 0.5) -> None:
        """记录责任违反"""
        violation = {
            "responsibility": responsibility,
            "severity": severity,
            "timestamp": "now",
            "context": ""
        }
        self._violation_history.append(violation)

    def get_fulfillment_rate(self) -> float:
        """计算责任履行率"""
        if not self._responsibilities:
            return 1.0
        
        fulfilled_count = sum(1 for r in self._responsibilities 
                             if self._fulfilled.get(r, False))
        return fulfilled_count / len(self._responsibilities)

    def get_violation_summary(self) -> List[Dict]:
        """获取违反记录摘要"""
        return [
            {
                "violation": v["responsibility"],
                "severity": v["severity"]
            }
            for v in self._violation_history
        ]

    def is_role_neglected(self, threshold: float = 0.3) -> bool:
        """检查角色是否被忽视（未履行责任）"""
        return self.get_fulfillment_rate() < (1 - threshold)


# 初始化说明
if __name__ == "__main__":
    print("Role component modules loaded.")