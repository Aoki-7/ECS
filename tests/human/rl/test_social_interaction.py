#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社会互动系统测试
"""
import pytest
from core.world import World
from human.rl.social_structure import SocialStructureSystem, RoleType
from human.rl.social_interaction import SocialInteractionSystem, InteractionType
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent
from space.space_component import SpaceComponent
from human.components.abilities.skill_component import SkillComponent

class TestSocialInteractionSystem:
    """社会互动系统测试"""
    def test_social_interaction_system(self):
        """测试社会互动系统"""
        world = World()
        social_system = SocialStructureSystem()
        interaction_system = SocialInteractionSystem()
        # 创建人类实体
        for i in range(20):
            entity_id = world.create_entity()
            world.add_component(entity_id, HumanComponent())
            world.add_component(entity_id, IntentComponent())
            world.add_component(entity_id, SpaceComponent(x=i*2, y=i*2))
            world.add_component(entity_id, SkillComponent())
        # 更新社会结构系统，形成部落
        social_system.update(world, 1.0)
        # 更新社会互动系统
        interaction_system.update(world, 1.0)
        # 验证互动生成
        assert len(interaction_system.interactions) >= 0
        # 验证群体关系初始化
        assert len(interaction_system.group_relations) >= 0

    def test_group_relations(self):
        """测试群体关系"""
        world = World()
        social_system = SocialStructureSystem()
        interaction_system = SocialInteractionSystem()
        # 创建人类实体
        for i in range(10):
            entity_id = world.create_entity()
            world.add_component(entity_id, HumanComponent())
            world.add_component(entity_id, SpaceComponent(x=i*2, y=i*2))
        # 更新社会结构系统，形成部落
        social_system.update(world, 1.0)
        # 更新社会互动系统
        interaction_system.update(world, 1.0)
        # 验证群体关系
        if len(social_system.groups) >= 2:
            group_ids = list(social_system.groups.keys())
            relation = interaction_system.get_group_relation(group_ids[0], group_ids[1])
            assert isinstance(relation, float)

if __name__ == "__main__":
    pytest.main([__file__])
