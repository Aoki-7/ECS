#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:leadership_system.py
@说明:领袖传承系统（从 TribeSystem 拆分）
@时间:2026/05/30
@@版本:1.0

职责：检查领袖是否健在，必要时选举新领袖
'''

import logging

from core.system import System
from core.world import World

from human.components.social.tribe_component import TribeComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from human.components.basic.identity_component import IdentityComponent
from biology.components.life_cycle_component import LifeCycleComponent
from human.components.social.social_component import SocialComponent
from core.systems.event_log_system import EventLog

logger = logging.getLogger(__name__)


class LeadershipSystem(System):
    tick_interval = 10  # 每10帧执行一次
    """领袖传承系统 — 部落领袖更替与选举"""

    priority = 40

    # 领袖选举评分权重
    AGE_WEIGHT = 2.0
    LOYALTY_WEIGHT = 0.5
    CONTRIBUTION_WEIGHT = 0.3
    FRIENDS_WEIGHT = 5.0
    # 新领袖上任忠诚度加成
    NEW_LEADER_LOYALTY_BONUS = 20.0

    def update(self, world: World, dt: float):
        current_time = world.get_time().total_hours
        for entity, (tribe,) in world.get_components(TribeComponent):
            self._check_leader_succession(world, tribe, current_time)

    def _check_leader_succession(self, world: World, tribe: TribeComponent, current_time: float):
        """检查领袖传承"""
        if tribe.leader_id is not None:
            leader = world.query_entity(tribe.leader_id)
            if leader is not None:
                return  # 领袖健在

        # 需要选新领袖
        if not tribe.member_ids:
            return

        best_candidate = None
        best_score = -1

        for member_id in tribe.member_ids:
            entity = world.query_entity(member_id)
            if entity is None:
                continue

            score = 0
            # 年长加分
            age = world.get_component(entity, LifeCycleComponent)
            if age:
                score += age.age * self.AGE_WEIGHT

            # 忠诚度高的加分
            membership = world.get_component(entity, TribeMembershipComponent)
            if membership:
                score += membership.loyalty * self.LOYALTY_WEIGHT
                score += membership.contribution * self.CONTRIBUTION_WEIGHT

            # 社交关系好的加分
            social = world.get_component(entity, SocialComponent)
            if social:
                score += len(social.friends) * self.FRIENDS_WEIGHT

            if score > best_score:
                best_score = score
                best_candidate = entity

        if best_candidate:
            # 旧领袖降级
            old_leader_id = tribe.leader_id
            if tribe.leader_id:
                old_leader = world.query_entity(tribe.leader_id)
                if old_leader:
                    old_mem = world.get_component(old_leader, TribeMembershipComponent)
                    if old_mem:
                        old_mem.role = "elder"

            # 新领袖上任
            tribe.set_leader(best_candidate.id)
            new_mem = world.get_component(best_candidate, TribeMembershipComponent)
            if new_mem:
                new_mem.role = "leader"
                new_mem.loyalty = min(100, new_mem.loyalty + self.NEW_LEADER_LOYALTY_BONUS)

            identity = world.get_component(best_candidate, IdentityComponent)
            name = identity.name if identity else f"Human_{best_candidate.id}"
            logger.debug(f"[LeadershipSystem] 部落 '{tribe.name}' 领袖更替: {name} (得分 {best_score:.0f})")

            EventLog.log(
                world, event_type="tribe_leader_change",
                description=f"部落 '{tribe.name}' 领袖更替为 {name}",
                entity_id=best_candidate.id,
                target_id=old_leader_id,
                location=tribe.home_territory,
                data={"tribe_name": tribe.name, "new_leader_name": name, "score": best_score},
                severity="warning"
            )
