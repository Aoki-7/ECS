#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:tribe_system.py
@说明:部落系统
@时间:2026/05/23
@版本:1.0

部落系统负责：
- 维护部落实体和成员关系
- 更新领地中心
- 领袖传承
- 忠诚度动态变化
- 外部成员招募（基于空间邻近和关系）
- 新生儿自动继承（由 ReproductionSystem 触发）
'''

import logging
import random
import math

from core.system import System

logger = logging.getLogger(__name__)
from core.world import World
from core.entity import Entity

from human.components.social.tribe_component import TribeComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from human.components.social.social_component import SocialComponent
from human.components.social.relationship_component import RelationshipComponent
from human.components.basic.identity_component import IdentityComponent
from human.components.basic.age_component import AgeComponent
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from core.event_log_component import EventLog


class TribeSystem(System):
    """
    部落系统
    
    管理部落的形成、成员关系、领袖传承和领地。
    """
    
    # 招募参数
    RECRUIT_DISTANCE = 8           # 招募距离阈值
    RECRUIT_RELATION_THRESHOLD = 15 # 关系分数招募阈值
    RECRUIT_CHANCE = 0.05          # 每帧招募概率
    
    # 忠诚度变化参数
    LOYALTY_SOCIAL_BONUS = 0.5     # 同部落社交增加忠诚度
    LOYALTY_LEADER_DISTANCE_PENALTY = 0.1  # 离领袖太远降低忠诚度
    LOYALTY_DECAY = 0.02           # 忠诚度自然衰减
    
    def __init__(self):
        self._initialized = False
        self._tribe_entity_cache = None
    
    def update(self, world: World, dt: float):
        if not self._initialized:
            self._init_tribes(world)
            self._initialized = True
        
        current_time = world.get_time().total_hours
        
        # 获取所有部落
        tribes = self._get_all_tribes(world)
        if not tribes:
            return
        
        for tribe_entity, tribe in tribes:
            # 1. 清理已不存在的成员
            self._cleanup_members(world, tribe)
            
            # 2. 更新领地中心
            self._update_territory(world, tribe)
            
            # 3. 检查领袖传承
            self._check_leader_succession(world, tribe, current_time)
            
            # 4. 更新成员忠诚度
            self._update_loyalties(world, tribe, dt)
            
            # 5. 尝试招募附近无部落成员
            self._try_recruit(world, tribe, current_time)
            
            # 6. 记录部落事件
            if tribe.get_member_count() >= 5 and not hasattr(tribe, '_milestone_5'):
                tribe._milestone_5 = True
                logger.info(f"[TribeSystem] 部落 '{tribe.name}' 达到5人里程碑")
    
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
        logger.info(f"[TribeSystem] 初始部落 '{tribe.name}' 成立，成员 {len(humans)} 人，领袖: {oldest.id if oldest else '无'}")
        EventLog.log(
            world, event_type="tribe_formed",
            description=f"部落 '{tribe.name}' 成立，成员 {len(humans)} 人",
            entity_id=oldest.id if oldest else None,
            location=tribe.home_territory,
            data={"tribe_name": tribe.name, "member_count": len(humans), "leader_id": oldest.id if oldest else None},
            severity="milestone"
        )
    
    def _get_all_tribes(self, world: World) -> list:
        """获取所有部落实体"""
        tribes = []
        for entity, [tribe] in world.get_components(TribeComponent):
            tribes.append((entity, tribe))
        return tribes
    
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
    
    def _update_territory(self, world: World, tribe: TribeComponent):
        """更新领地中心为所有成员的平均位置"""
        if not tribe.member_ids:
            return
        
        total_x, total_y = 0, 0
        count = 0
        for member_id in tribe.member_ids:
            entity = world.query_entity(member_id)
            if entity:
                space = world.get_component(entity, SpaceComponent)
                if space:
                    total_x += space.x
                    total_y += space.y
                    count += 1
        
        if count > 0:
            # 平滑更新领地中心
            new_x = total_x / count
            new_y = total_y / count
            old_x, old_y = tribe.home_territory
            tribe.home_territory = (
                old_x * 0.9 + new_x * 0.1,
                old_y * 0.9 + new_y * 0.1
            )
    
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
            age = world.get_component(entity, AgeComponent)
            if age:
                score += age.age * 2
            
            # 忠诚度高的加分
            membership = world.get_component(entity, TribeMembershipComponent)
            if membership:
                score += membership.loyalty * 0.5
                score += membership.contribution * 0.3
            
            # 社交关系好的加分
            social = world.get_component(entity, SocialComponent)
            if social:
                score += len(social.friends) * 5
            
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
                new_mem.loyalty = min(100, new_mem.loyalty + 20)
            
            identity = world.get_component(best_candidate, IdentityComponent)
            name = identity.name if identity else f"Human_{best_candidate.id}"
            logger.info(f"[TribeSystem] 部落 '{tribe.name}' 领袖更替: {name} (得分 {best_score:.0f})")
            
            # 记录到全局事件日志
            EventLog.log(
                world, event_type="tribe_leader_change",
                description=f"部落 '{tribe.name}' 领袖更替为 {name}",
                entity_id=best_candidate.id,
                target_id=old_leader_id,
                location=tribe.home_territory,
                data={"tribe_name": tribe.name, "new_leader_name": name, "score": best_score},
                severity="warning"
            )
            
            # 记录到记忆
            for member_id in tribe.member_ids:
                entity = world.query_entity(member_id)
                if entity:
                    memory = world.get_component(entity, MemoryComponent)
                    if memory:
                        memory.add_event(
                            current_time, "tribe_leader_change",
                            f"部落 '{tribe.name}' 选举了新领袖 {name}",
                            impact=0.3,
                            location=tribe.home_territory
                        )
    
    def _update_loyalties(self, world: World, tribe: TribeComponent, dt: float):
        """更新成员忠诚度"""
        leader = world.query_entity(tribe.leader_id) if tribe.leader_id else None
        leader_space = world.get_component(leader, SpaceComponent) if leader else None
        
        for member_id in tribe.member_ids:
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
                    if dist < 10:
                        membership.add_loyalty(self.LOYALTY_SOCIAL_BONUS * dt)
                    elif dist > 30:
                        membership.add_loyalty(-self.LOYALTY_LEADER_DISTANCE_PENALTY * dt)
            
            # 自然衰减
            membership.add_loyalty(-self.LOYALTY_DECAY * dt)
            
            # 贡献值自然微增（存活奖励）
            membership.contribution += 0.01 * dt
    
    def _try_recruit(self, world: World, tribe: TribeComponent, current_time: float):
        """尝试招募附近的无部落成员"""
        if tribe.get_member_count() >= 20:
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
            other_membership.tribe_id = world.query_entity(tribe).id if world.query_entity(tribe) else None
            other_membership.role = "member"
            other_membership.joined_time = current_time
            other_membership.loyalty = 40.0 + best_relation * 0.3
            
            identity = world.get_component(entity, IdentityComponent)
            name = identity.name if identity else f"Human_{entity.id}"
            logger.info(f"[TribeSystem] {name} 加入部落 '{tribe.name}'")
            
            # 记录到全局事件日志
            EventLog.log(
                world, event_type="joined_tribe",
                description=f"{name} 加入部落 '{tribe.name}'",
                entity_id=entity.id,
                location=(space.x, space.y),
                data={"tribe_name": tribe.name, "member_name": name},
                severity="info"
            )
            
            # 记录到记忆
            memory = world.get_component(entity, MemoryComponent)
            if memory:
                memory.add_event(
                    current_time, "joined_tribe",
                    f"加入部落 '{tribe.name}'",
                    impact=0.4,
                    location=(space.x, space.y)
                )
    
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
