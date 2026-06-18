#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:pairing_system.py
@说明:配对系统
@时间:2026/04/14
@作者:GitHub Copilot
@版本:1.0
'''

from core.system import System
from core.world import World
from identity.event_log_system import EventLog

from human.components.cognitive.intent_component import IntentComponent, IntentType
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.social.relationship_component import RelationshipComponent, RelationshipStatus
from human.components.social.social_component import SocialComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.components.gender_component import GenderComponent, Gender
from human.components.action.action_component import ActionComponent, ActionType


class PairingSystem(System):
    tick_interval = 5  # 每5帧执行一次
    """
    配对系统
    基于社会需求、年龄和性别寻找伴侣。
    """

    def update(self, world: World, dt: float):
        # 收集所有单身人类，同时按性别分组并缓存部落信息
        males = []
        females = []
        # entity_id -> (entity, tribe_id) 快速查找缓存
        tribe_cache = {}
        
        for entity, (intent, needs, relation, age, gender) in world.get_components(
            IntentComponent, PhysiologyNeedsComponent, RelationshipComponent, LifeCycleComponent, GenderComponent
        ):
            if not intent or not needs or not relation or not age or not gender:
                continue

            if relation.status == RelationshipStatus.SINGLE and self._is_reproductive_age(age):
                # 提前过滤：只有社交需求适中且无紧急生存意图的才进入候选池
                if (needs.social < 60 and
                    intent.intent not in (IntentType.EAT, IntentType.DRINK, IntentType.SLEEP)):
                    mem = world.get_component(entity, TribeMembershipComponent)
                    tribe_id = mem.tribe_id if mem else None
                    tribe_cache[entity.id] = (entity, tribe_id)
                    info = (entity, intent, needs, relation, age, gender, tribe_id)
                    if gender.gender == Gender.MALE:
                        males.append(info)
                    else:
                        females.append(info)

        if not males or not females:
            return

        # 追踪本帧已配对的实体
        paired_this_frame = set()

        # 为每个单身男性寻找配对（减少一半迭代量）
        for m_info in males:
            entity, intent, needs, relation, age, gender, m_tribe = m_info
            if entity in paired_this_frame:
                continue

            partner = self._find_partner_fast(m_info, females, paired_this_frame, tribe_cache)
            if partner:
                p_entity, _, _, p_relation, _, _, _ = partner
                self.form_relationship(world, entity, partner, relation, p_relation)
                intent.intent = IntentType.PAIR
                intent.target_entity = p_entity
                paired_this_frame.add(entity)
                paired_this_frame.add(p_entity)

    def _find_partner_fast(self, self_info, opposite_pool, paired_this_frame, tribe_cache):
        """优化的配对查找：直接遍历异性候选池，部落优先但不排序"""
        self_entity, _, _, _, _, _, self_tribe = self_info
        best_same_tribe = None
        best_other = None

        for info in opposite_pool:
            candidate = info[0]
            if candidate == self_entity or candidate in paired_this_frame:
                continue
            if info[3].status != RelationshipStatus.SINGLE:
                continue

            c_tribe = info[6]
            if self_tribe is not None and c_tribe == self_tribe:
                if best_same_tribe is None:
                    best_same_tribe = info
            else:
                if best_other is None:
                    best_other = info

            # 已经找到同部落候选，可以提前返回
            if best_same_tribe is not None:
                return best_same_tribe

        return best_same_tribe or best_other

    def _is_reproductive_age(self, age) -> bool:
        """判断是否为生育年龄"""
        # 防御：如果 age 是对象，尝试获取 age 属性
        if hasattr(age, 'age'):
            age = age.age
        elif hasattr(age, 'value'):
            age = age.value
        elif not isinstance(age, (int, float)):
            return False
        return 12 <= age <= 65

    def form_relationship(self, world, entity1, entity2_info, relation1: RelationshipComponent, relation2: RelationshipComponent):
        """建立关系"""
        entity2 = entity2_info[0]
        relation1.status = RelationshipStatus.MARRIED
        relation1.partner_id = entity2
        relation2.relationship_strength = 70.0

        relation2.status = RelationshipStatus.MARRIED
        relation2.partner_id = entity1
        relation2.relationship_strength = 50.0
        
        # 在社交组件中将对方标记为家庭成员
        social1 = world.get_component(entity1, SocialComponent)
        social2 = world.get_component(entity2, SocialComponent)
        if social1:
            if hasattr(social1, 'family') and entity2.id not in social1.family:
                social1.family.append(entity2.id)
            if hasattr(social1, 'update_relation'):
                social1.update_relation(entity2.id, 50)
            else:
                social1.relations[entity2.id] = 50
        if social2:
            if hasattr(social2, 'family') and entity1.id not in social2.family:
                social2.family.append(entity1.id)
            if hasattr(social2, 'update_relation'):
                social2.update_relation(entity1.id, 50)
            else:
                social2.relations[entity1.id] = 50
        
        # 记录事件日志
        try:
            EventLog.log(
                world, event_type="pairing",
                description=f"实体 {entity1.id} 与 {entity2.id} 结为伴侣",
                entity_id=entity1.id,
                target_id=entity2.id,
                severity="info"
            )
        except Exception as e:
            # EventLog.log 可能不存在，静默忽略
            pass