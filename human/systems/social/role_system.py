#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
RoleSystem - 角色管理系统

职责：
- 管理 RoleComponent 的增删改查
- 处理 IdentityShiftComponent 的情境切换
- 追踪 ResponsibilityComponent 的责任履行与违反

原位于 role_component.py 中的业务逻辑已迁移至此。
"""

from typing import Dict, List, Optional
from core.system import System
from core.world import World
from core.entity import Entity
from human.components.society.role_component import (
    RoleComponent, RoleType, Role,
    IdentityShiftComponent, ResponsibilityComponent
)


class RoleSystem(System):
    tick_interval = 5  # 每5帧执行一次
    """角色管理系统，处理实体在社会结构中的角色、身份与责任。"""

    priority = 30  # 与人类核心系统同级

    # ═══════════════════════════════════════════════
    # RoleComponent 业务逻辑
    # ═══════════════════════════════════════════════

    @staticmethod
    def add_role(world: World, entity: Entity, role_type: RoleType,
                 title: str,
                 description: str = "",
                 responsibilities: List[str] = None,
                 importance: float = 50.0) -> Role:
        """为实体添加角色"""
        role_comp = world.get_component(entity, RoleComponent)
        if role_comp is None:
            role_comp = RoleComponent()
            world.add_component(entity, role_comp)

        role = Role(
            title=title,
            description=description,
            responsibility_list=responsibilities or [],
            importance=importance
        )
        role_comp._roles[role_type].append(role)
        return role

    @staticmethod
    def get_primary_role(world: World, entity: Entity, role_type: RoleType) -> Optional[Role]:
        """获取某类型的主要角色（重要性最高的）"""
        role_comp = world.get_component(entity, RoleComponent)
        if role_comp is None:
            return None
        roles = role_comp._roles[role_type]
        if not roles:
            return None
        return max(roles, key=lambda r: r.importance)

    @staticmethod
    def get_active_role(world: World, entity: Entity, context: str) -> Optional[Role]:
        """根据情境获取当前活跃角色"""
        role_comp = world.get_component(entity, RoleComponent)
        if role_comp is None:
            return None

        keywords = {
            "家庭": [RoleType.FAMILY],
            "工作": [RoleType.OCCUPATION],
            "社区": [RoleType.COMMUNITY],
            "朋友聚会": [RoleType.SOCIAL],
        }

        if any(kw in context for kw in keywords.get("家庭", [])):
            return RoleSystem.get_primary_role(world, entity, RoleType.FAMILY)
        elif any(kw in context for kw in keywords.get("工作", [])):
            return RoleSystem.get_primary_role(world, entity, RoleType.OCCUPATION)

        return None

    @staticmethod
    def get_all_roles(world: World, entity: Entity) -> List[Role]:
        """获取所有角色的扁平列表"""
        role_comp = world.get_component(entity, RoleComponent)
        if role_comp is None:
            return []
        result = []
        for roles in role_comp._roles.values():
            result.extend(roles)
        return result

    @staticmethod
    def has_conflict(entity: Entity, role1: Role, role2: Role) -> bool:
        """检查两个角色是否存在责任冲突"""
        resp1 = role1.responsibility_list
        resp2 = role2.responsibility_list

        conflict_pairs = [
            ("照顾家人", "加班工作"),
            ("遵守命令", "坚持原则")
        ]

        for r1 in resp1:
            for r2 in resp2:
                if any((r1, r2) == pair for pair in conflict_pairs):
                    return True
        return False

    # ═══════════════════════════════════════════════
    # IdentityShiftComponent 业务逻辑
    # ═══════════════════════════════════════════════

    @staticmethod
    def switch_identity(world: World, entity: Entity, context: str) -> Dict:
        """根据情境切换身份显示"""
        shift = world.get_component(entity, IdentityShiftComponent)
        if shift is None:
            return {"display": "default"}

        if any(kw in context for kw in ["公众", "正式", "工作"]):
            return {"display": shift._public}
        else:
            return {"display": shift._private}

    @staticmethod
    def get_identity_mask(world: World, entity: Entity) -> str:
        """获取当前情境的身份面具"""
        shift = world.get_component(entity, IdentityShiftComponent)
        if shift is None:
            return "default"
        return shift._public if shift._public else "default"

    # ═══════════════════════════════════════════════
    # ResponsibilityComponent 业务逻辑
    # ═══════════════════════════════════════════════

    @staticmethod
    def record_fulfillment(world: World, entity: Entity, responsibility: str) -> None:
        """记录责任履行"""
        resp_comp = world.get_component(entity, ResponsibilityComponent)
        if resp_comp is None:
            return
        if responsibility in resp_comp._responsibilities:
            resp_comp._fulfilled[responsibility] = True

    @staticmethod
    def record_violation(world: World, entity: Entity, responsibility: str, severity: float = 0.5) -> None:
        """记录责任违反"""
        resp_comp = world.get_component(entity, ResponsibilityComponent)
        if resp_comp is None:
            return
        violation = {
            "responsibility": responsibility,
            "severity": severity,
            "timestamp": "now",
            "context": ""
        }
        resp_comp._violation_history.append(violation)

    @staticmethod
    def get_fulfillment_rate(world: World, entity: Entity) -> float:
        """计算责任履行率"""
        resp_comp = world.get_component(entity, ResponsibilityComponent)
        if resp_comp is None or not resp_comp._responsibilities:
            return 1.0

        fulfilled_count = sum(
            1 for r in resp_comp._responsibilities
            if resp_comp._fulfilled.get(r, False)
        )
        return fulfilled_count / len(resp_comp._responsibilities)

    @staticmethod
    def get_violation_summary(world: World, entity: Entity) -> List[Dict]:
        """获取违反记录摘要"""
        resp_comp = world.get_component(entity, ResponsibilityComponent)
        if resp_comp is None:
            return []
        return [
            {"violation": v["responsibility"], "severity": v["severity"]}
            for v in resp_comp._violation_history
        ]

    @staticmethod
    def is_role_neglected(world: World, entity: Entity, threshold: float = 0.3) -> bool:
        """检查角色是否被忽视（未履行责任）"""
        return RoleSystem.get_fulfillment_rate(world, entity) < (1 - threshold)

    # ═══════════════════════════════════════════════
    # System update
    # ═══════════════════════════════════════════════

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)
        # 角色重要性自然衰减，新责任添加未履行记录
        for entity, (role_comp) in world.get_components(RoleComponent):
            for role_type, roles in role_comp._roles.items():
                for role in roles:
                    if role.importance > 10.0:
                        role.importance = max(10.0, role.importance - 0.05)

            resp_comp = world.get_component(entity, ResponsibilityComponent)
            if resp_comp is not None:
                for resp in resp_comp.responsibilities:
                    if resp not in resp_comp.fulfilled:
                        resp_comp.fulfilled[resp] = False
