#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:tribe_system.py
@说明:部落系统（协调器版）
@时间:2026/05/23
@版本:2.0

职责：
- 初始化部落（首次运行时）
- 清理已死亡/移除的成员
- 新生儿自动继承部落（由 ReproductionSystem 触发）
- 提供部落统计查询

原 _update_territory / _check_leader_succession / _update_loyalties / _try_recruit
已分别拆分为 TerritorySystem / LeadershipSystem / LoyaltySystem / RecruitSystem。
'''

import logging
import random

from core.system import System
from core.world import World
from core.entity import Entity

logger = logging.getLogger(__name__)

from human.components.social.tribe_component import TribeComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from human.components.basic.identity_component import IdentityComponent
from biology.components.age_component import AgeComponent
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from core.systems.event_log_system import EventLog


class TribeSystem(System):
    """
    部落系统协调器
    
    负责部落初始化、成员清理和新生儿分配。
    具体的领地维护、领袖选举、忠诚度更新、成员招募
    由 TerritorySystem / LeadershipSystem / LoyaltySystem / RecruitSystem 处理。
    """

    priority = 43  # 在拆分后的子系统之后执行清理

    def __init__(self):
        self._initialized = False
        self._tribe_entity_cache = None

    def update(self, world: World, dt: float):
        if not self._initialized:
            self._init_tribes(world)
            self._initialized = True

        # 获取所有部落并清理无效成员
        for entity, (tribe,) in world.get_components(TribeComponent):
            self._cleanup_members(world, tribe)

            # 记录部落里程碑
            if tribe.get_member_count() >= 5 and not hasattr(tribe, '_milestone_5'):
                tribe._milestone_5 = True
                logger.debug(f"[TribeSystem] 部落 '{tribe.name}' 达到5人里程碑")

    def _init_tribes(self, world: World):
        """初始化：为所有无部落的人类创建一个初始部落"""
        humans = []
        for entity, _ in world.get_components(TribeMembershipComponent):
            humans.append(entity)

        if not humans:
            return

        # 创建部落实体
        tribe_entity = world.create_entity()
        tribe = TribeComponent(name="初始部落")
        world.add_component(tribe_entity, tribe)

        # 计算初始领地中心
        total_x, total_y = 0, 0
        for entity in humans:
            space = world.get_component(entity, SpaceComponent)
            if space:
                total_x += space.x
                total_y += space.y

        tribe.home_territory = (total_x / len(humans), total_y / len(humans))
        tribe.formed_time = world.get_time().total_hours

        # 选择最年长者为领袖
        oldest = None
        max_age = -1
        for entity in humans:
            age = world.get_component(entity, AgeComponent)
            if age and age.age > max_age:
                max_age = age.age
                oldest = entity

        # 添加所有成员
        for entity in humans:
            membership = world.get_component(entity, TribeMembershipComponent)
            if membership:
                tribe.add_member(entity.id)
                membership.tribe_id = tribe_entity.id
                membership.joined_time = world.get_time().total_hours
                if entity == oldest:
                    membership.role = "leader"
                    tribe.set_leader(entity.id)
                else:
                    membership.role = "member"
                membership.loyalty = 60.0 + random.uniform(-10, 10)

        self._tribe_entity_cache = tribe_entity
        logger.debug(f"[TribeSystem] 初始部落 '{tribe.name}' 成立，成员 {len(humans)} 人，领袖: {oldest.id if oldest else '无'}")
        EventLog.log(
            world, event_type="tribe_formed",
            description=f"部落 '{tribe.name}' 成立，成员 {len(humans)} 人",
            entity_id=oldest.id if oldest else None,
            location=tribe.home_territory,
            data={"tribe_name": tribe.name, "member_count": len(humans), "leader_id": oldest.id if oldest else None},
            severity="milestone"
        )

    def _cleanup_members(self, world: World, tribe: TribeComponent):
        """清理已不存在的成员"""
        valid_members = []
        for member_id in tribe.member_ids:
            entity = world.query_entity(member_id)
            if entity is not None:
                valid_members.append(member_id)

        removed = len(tribe.member_ids) - len(valid_members)
        if removed > 0:
            tribe.member_ids = valid_members
            if tribe.leader_id not in valid_members:
                tribe.leader_id = None

    def assign_birth_tribe(self, world: World, child_entity: Entity, parent_entity: Entity,
                           current_time: float):
        """
        由 ReproductionSystem 调用：给新生儿分配部落。
        继承母亲的部落。
        """
        parent_membership = world.get_component(parent_entity, TribeMembershipComponent)
        if not parent_membership or not parent_membership.is_member():
            return

        tribe_entity = world.query_entity(parent_membership.tribe_id)
        if tribe_entity is None:
            return

        tribe = world.get_component(tribe_entity, TribeComponent)
        if tribe is None:
            return

        child_membership = world.get_component(child_entity, TribeMembershipComponent)
        if child_membership is None:
            return

        tribe.add_member(child_entity.id)
        child_membership.tribe_id = tribe_entity.id
        child_membership.role = "member"
        child_membership.joined_time = current_time
        child_membership.loyalty = 50.0 + parent_membership.loyalty * 0.3

        # 父母贡献值增加
        parent_membership.add_contribution(10)

        # 记录到全局事件日志
        child_identity = world.get_component(child_entity, IdentityComponent)
        child_name = child_identity.name if child_identity else f"Human_{child_entity.id}"
        EventLog.log(
            world, event_type="tribe_birth",
            description=f"部落 '{tribe.name}' 迎来新生儿 {child_name}",
            entity_id=child_entity.id,
            target_id=parent_entity.id,
            location=tribe.home_territory,
            data={"tribe_name": tribe.name, "child_name": child_name},
            severity="info"
        )

        # 记录到记忆
        memory = world.get_component(parent_entity, MemoryComponent)
        if memory:
            memory.add_event(
                current_time, "tribe_birth",
                f"部落 '{tribe.name}' 迎来了新生儿 {child_name}",
                impact=0.5,
                location=tribe.home_territory
            )

    def get_tribe_stats(self, world: World, tribe_entity: Entity) -> dict:
        """获取部落统计信息"""
        tribe = world.get_component(tribe_entity, TribeComponent)
        if not tribe:
            return {}

        avg_loyalty = 0
        member_count = tribe.get_member_count()

        for member_id in tribe.member_ids:
            entity = world.query_entity(member_id)
            if entity:
                membership = world.get_component(entity, TribeMembershipComponent)
                if membership:
                    avg_loyalty += membership.loyalty

        if member_count > 0:
            avg_loyalty /= member_count

        return {
            "name": tribe.name,
            "members": member_count,
            "leader_id": tribe.leader_id,
            "territory": tribe.home_territory,
            "avg_loyalty": avg_loyalty,
            "culture": tribe.culture,
        }
