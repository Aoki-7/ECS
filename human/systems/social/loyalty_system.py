#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:loyalty_system.py
@说明:忠诚度系统（从 TribeSystem 拆分）
@时间:2026/05/30
@版本:1.0

职责：更新部落成员的忠诚度动态变化
'''

import math

from core.system import System
from core.world import World

from human.components.social.tribe_component import TribeComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from human.systems.social.tribe_system import TribeSystem
from space.space_component import SpaceComponent


class LoyaltySystem(System):
    tick_interval = 10  # 每10帧执行一次
    """忠诚度系统 — 部落成员归属感动态变化"""

    priority = 41

    # 忠诚度变化参数
    LOYALTY_SOCIAL_BONUS = 0.5     # 同部落社交增加忠诚度
    LOYALTY_LEADER_DISTANCE_PENALTY = 0.1  # 离领袖太远降低忠诚度
    LOYALTY_DECAY = 0.02           # 忠诚度自然衰减
    LEADER_PROXIMITY_THRESHOLD = 10.0  # 领袖附近判定距离
    LEADER_DISTANCE_THRESHOLD = 30.0   # 离领袖太远判定距离
    CONTRIBUTION_SURVIVAL_BONUS = 0.01 # 存活贡献值增长 /小时

    def update(self, world: World, dt: float):
        for entity, (tribe,) in world.get_components(TribeComponent):
            self._update_loyalties(world, tribe, dt)

    def _update_loyalties(self, world: World, tribe: TribeComponent, dt: float):
        """更新成员忠诚度"""
        leader = world.query_entity(tribe.leader_id) if tribe.leader_id else None
        leader_space = world.get_component(leader, SpaceComponent) if leader else None

        for member_id in TribeSystem.get_member_ids(tribe):
            entity = world.query_entity(member_id)
            if entity is None:
                continue

            membership = world.get_component(entity, TribeMembershipComponent)
            if membership is None:
                continue

            # 领袖附近增加忠诚度
            if leader_space:
                space = world.get_component(entity, SpaceComponent)
                if space:
                    dist = math.hypot(space.x - leader_space.x, space.y - leader_space.y)
                    if dist < self.LEADER_PROXIMITY_THRESHOLD:
                        TribeSystem.add_loyalty(membership, self.LOYALTY_SOCIAL_BONUS * dt)
                    elif dist > self.LEADER_DISTANCE_THRESHOLD:
                        TribeSystem.add_loyalty(membership, -self.LOYALTY_LEADER_DISTANCE_PENALTY * dt)

            # 自然衰减
            TribeSystem.add_loyalty(membership, -self.LOYALTY_DECAY * dt)

            # 贡献值自然微增（存活奖励）
            membership.contribution += self.CONTRIBUTION_SURVIVAL_BONUS * dt
