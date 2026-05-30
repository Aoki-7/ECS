#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:recruit_system.py
@说明:招募系统（从 TribeSystem 拆分）
@时间:2026/05/30
@版本:1.0

职责：尝试招募附近的无部落成员
'''

import random
import math
import logging

from core.system import System
from core.world import World

from human.components.social.tribe_component import TribeComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from human.components.social.social_component import SocialComponent
from human.components.basic.identity_component import IdentityComponent
from space.space_component import SpaceComponent
from core.systems.event_log_system import EventLog

logger = logging.getLogger(__name__)


class RecruitSystem(System):
    """招募系统 — 部落对外扩张成员"""

    priority = 42

    # 招募参数
    RECRUIT_DISTANCE = 8.0           # 招募距离阈值
    RECRUIT_RELATION_THRESHOLD = 15.0 # 关系分数招募阈值
    RECRUIT_CHANCE = 0.05            # 每帧招募概率
    MAX_TRIBE_SIZE = 20              # 部落最大人数
    NEW_MEMBER_BASE_LOYALTY = 40.0   # 新成员基础忠诚度
    NEW_MEMBER_RELATION_LOYALTY_FACTOR = 0.3  # 关系对忠诚度的影响系数

    def update(self, world: World, dt: float):
        current_time = world.get_time().total_hours
        for entity, (tribe,) in world.get_components(TribeComponent):
            self._try_recruit(world, tribe, current_time)

    def _try_recruit(self, world: World, tribe: TribeComponent, current_time: float):
        """尝试招募附近的无部落成员"""
        if tribe.get_member_count() >= self.MAX_TRIBE_SIZE:
            return  # 部落太大不再招募

        center_x, center_y = tribe.home_territory

        for entity, [space, other_membership] in world.get_components(
            SpaceComponent, TribeMembershipComponent
        ):
            # 只招募无部落者
            if other_membership.is_member():
                continue

            # 距离检查
            dist = math.hypot(space.x - center_x, space.y - center_y)
            if dist > self.RECRUIT_DISTANCE:
                continue

            # 关系检查：是否认识任何部落成员
            social = world.get_component(entity, SocialComponent)
            known_member = False
            best_relation = -100
            if social:
                for member_id in tribe.member_ids:
                    if member_id in social.relations:
                        known_member = True
                        best_relation = max(best_relation, social.relations[member_id])

            if not known_member:
                continue

            # 关系好才招募
            if best_relation < self.RECRUIT_RELATION_THRESHOLD:
                continue

            # 概率招募
            if random.random() > self.RECRUIT_CHANCE:
                continue

            # 执行招募
            tribe.add_member(entity.id)
            other_membership.tribe_id = entity.id if world.query_entity(tribe) else None
            other_membership.role = "member"
            other_membership.joined_time = current_time
            other_membership.loyalty = self.NEW_MEMBER_BASE_LOYALTY + best_relation * self.NEW_MEMBER_RELATION_LOYALTY_FACTOR

            identity = world.get_component(entity, IdentityComponent)
            name = identity.name if identity else f"Human_{entity.id}"
            logger.debug(f"[RecruitSystem] {name} 加入部落 '{tribe.name}'")

            EventLog.log(
                world, event_type="joined_tribe",
                description=f"{name} 加入部落 '{tribe.name}'",
                entity_id=entity.id,
                location=(space.x, space.y),
                data={"tribe_name": tribe.name, "member_name": name},
                severity="info"
            )

            # 记录到记忆
            from human.components.cognitive.memory_component import MemoryComponent
            memory = world.get_component(entity, MemoryComponent)
            if memory:
                memory.add_event(
                    current_time, "joined_tribe",
                    f"加入部落 '{tribe.name}'",
                    impact=0.4,
                    location=(space.x, space.y)
                )
