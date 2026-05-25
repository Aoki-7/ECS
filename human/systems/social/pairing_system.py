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
from core.event_log_component import EventLog

from human.components.cognitive.intent_component import IntentComponent, IntentType
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.social.relationship_component import RelationshipComponent, RelationshipStatus
from human.components.social.social_component import SocialComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from human.components.basic.age_component import AgeComponent
from human.components.basic.gender_component import GenderComponent, Gender
from human.components.action.action_component import ActionComponent, ActionType


class PairingSystem(System):
    """
    配对系统
    基于社会需求、年龄和性别寻找伴侣。
    """

    def update(self, world: World, dt):
        # 收集所有单身人类
        singles = []
        for entity, (intent, needs, relation, age, gender) in world.get_components(
            IntentComponent, PhysiologyNeedsComponent, RelationshipComponent, AgeComponent, GenderComponent
        ):
            if not intent or not needs or not relation or not age or not gender:
                continue

            intent: IntentComponent
            needs: PhysiologyNeedsComponent
            relation: RelationshipComponent
            age: AgeComponent
            gender: GenderComponent

            if relation.status == RelationshipStatus.SINGLE and age.is_reproductive_age():
                singles.append((entity, intent, needs, relation, age, gender))

        # 追踪本帧已配对的实体，避免一人被多人配对
        paired_this_frame = set()

        # 为每个单身者寻找配对机会
        for entity, intent, needs, relation, age, gender in singles:
            # 跳过本帧已配对的人
            if entity in paired_this_frame:
                continue

            # 只有当社会需求中等偏低且没有紧急生存意图时，才触发配对
            if (needs.social < 60 and
                intent.intent not in (IntentType.EAT, IntentType.DRINK, IntentType.SLEEP)):
                # 寻找合适的伴侣（排除已配对的候选者）
                partner = self.find_partner(entity, gender.gender, singles, paired_this_frame, world)
                if partner:
                    partner_entity = partner[0]
                    # 建立关系
                    self.form_relationship(world, entity, partner, relation, partner[3])
                    # 设置意图为配对
                    intent.intent = IntentType.PAIR
                    intent.target_entity = partner_entity
                    # 标记双方已配对
                    paired_this_frame.add(entity)
                    paired_this_frame.add(partner_entity)

    def find_partner(self, self_entity, self_gender, singles, paired_this_frame=None, world=None):
        """寻找合适的伴侣（排除已配对的人，同部落优先）"""
        opposite_gender = Gender.FEMALE if self_gender == Gender.MALE else Gender.MALE
        candidates = []
        
        # 获取自己的部落
        self_tribe = None
        if world:
            self_mem = world.get_component(self_entity, TribeMembershipComponent)
            if self_mem:
                self_tribe = self_mem.tribe_id
        
        for s in singles:
            candidate_entity = s[0]
            candidate_relation = s[3]
            # 排除自己、已配对的人、以及非单身状态的人
            if candidate_entity == self_entity:
                continue
            if paired_this_frame and candidate_entity in paired_this_frame:
                continue
            if candidate_relation.status != RelationshipStatus.SINGLE:
                continue
            if s[5].gender == opposite_gender:
                candidates.append(s)
        
        if not candidates:
            return None
        
        # 同部落优先排序
        if world and self_tribe is not None:
            def _tribe_priority(s):
                mem = world.get_component(s[0], TribeMembershipComponent)
                if mem and mem.tribe_id == self_tribe:
                    return 0  # 同部落优先
                return 1
            candidates.sort(key=_tribe_priority)
        
        return candidates[0]

    def form_relationship(self, world, entity1, entity2_info, relation1: RelationshipComponent, relation2: RelationshipComponent):
        """建立关系"""
        entity2, _, _, _, _, _ = entity2_info
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
            if entity2.id not in social1.family:
                social1.family.append(entity2.id)
            social1.update_relation(entity2.id, 50)
        if social2:
            if entity1.id not in social2.family:
                social2.family.append(entity1.id)
            social2.update_relation(entity1.id, 50)
        
        # 记录事件日志
        EventLog.log(
            world, event_type="pairing",
            description=f"实体 {entity1.id} 与 {entity2.id} 结为伴侣",
            entity_id=entity1.id,
            target_id=entity2.id,
            severity="info"
        )