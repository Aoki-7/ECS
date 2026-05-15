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

from human.components.cognitive.intent_component import IntentComponent, IntentType
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.social.relationship_component import RelationshipComponent, RelationshipStatus
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

        # 为每个单身者寻找配对机会
        for entity, intent, needs, relation, age, gender in singles:
            # 只有当社会需求高且没有其他意图时，才触发配对
            if needs.social < 30 and intent.intent == IntentType.IDLE:
                # 寻找合适的伴侣
                partner = self.find_partner(entity, gender.gender, singles)
                if partner:
                    # 建立关系
                    self.form_relationship(world, entity, partner, relation, partner[3])
                    # 设置意图为配对
                    intent.intent = IntentType.PAIR
                    intent.target_entity = partner[0]

    def find_partner(self, self_entity, self_gender, singles):
        """寻找合适的伴侣"""
        opposite_gender = Gender.FEMALE if self_gender == Gender.MALE else Gender.MALE
        candidates = [s for s in singles if s[5].gender == opposite_gender and s[0] != self_entity]
        if candidates:
            # 简单选择第一个（可以扩展为更复杂的匹配逻辑）
            return candidates[0]
        return None

    def form_relationship(self, world, entity1, entity2_info, relation1: RelationshipComponent, relation2: RelationshipComponent):
        """建立关系"""
        entity2, _, _, _, _, _ = entity2_info
        relation1.status = RelationshipStatus.MARRIED
        relation1.partner_id = entity2
        relation2.relationship_strength = 70.0

        relation2.status = RelationshipStatus.MARRIED
        relation2.partner_id = entity1
        relation2.relationship_strength = 50.0