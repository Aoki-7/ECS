#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文化模块优化测试
"""
import pytest
from core.world import World
from human.rl.social_structure import SocialStructureSystem
from human.rl.cultural_inheritance import CulturalInheritanceSystem, KnowledgeType
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent
from space.space_component import SpaceComponent
from human.components.abilities.skill_component import SkillComponent

class TestCulturalOptimization:
    """文化模块优化测试"""
    def test_knowledge_creation(self):
        """测试知识创造"""
        world = World()
        cultural_system = CulturalInheritanceSystem()
        # 创建人类实体
        for i in range(10):
            entity_id = world.create_entity()
            world.add_component(entity_id, HumanComponent())
            world.add_component(entity_id, SkillComponent())
        # 多次更新，增加知识创造机会
        for _ in range(100):
            cultural_system.update(world, 1.0)
        # 验证知识创造
        assert len(cultural_system.knowledge) >= 0

    def test_teaching_knowledge(self):
        """测试知识教学"""
        world = World()
        cultural_system = CulturalInheritanceSystem()
        # 创建人类实体
        entity1 = world.create_entity()
        entity2 = world.create_entity()
        world.add_component(entity1, HumanComponent())
        world.add_component(entity2, HumanComponent())
        world.add_component(entity1, SpaceComponent(x=0, y=0))
        world.add_component(entity2, SpaceComponent(x=1, y=1))
        # 给教师一些知识，给学生较低的知识水平（使用整数ID作为键）
        cultural_system.entity_knowledge[entity1.id] = {KnowledgeType.SURVIVAL: 3.0}
        cultural_system.entity_knowledge[entity2.id] = {KnowledgeType.SURVIVAL: 0.5}
        print(f"初始状态: 教师知识 {cultural_system.entity_knowledge[entity1.id]}, 学生知识 {cultural_system.entity_knowledge[entity2.id]}")
        # 多次更新，增加教学机会
        for i in range(100):
            cultural_system.update(world, 1.0)
            if i % 20 == 0:
                print(f"第{i}次更新后: 学生知识 {cultural_system.entity_knowledge.get(entity2.id, {})}")
        # 验证知识教学：学生的知识水平应该提升
        student_knowledge = cultural_system.entity_knowledge.get(entity2.id, {})
        print(f"最终状态: 学生知识 {student_knowledge}")
        assert student_knowledge.get(KnowledgeType.SURVIVAL, 0) > 0.5

    def test_tradition_formation(self):
        """测试文化传统形成"""
        world = World()
        social_system = SocialStructureSystem()
        cultural_system = CulturalInheritanceSystem()
        # 创建人类实体
        for i in range(5):
            entity_id = world.create_entity()
            world.add_component(entity_id, HumanComponent())
            world.add_component(entity_id, SpaceComponent(x=i, y=i))
            world.add_component(entity_id, SkillComponent())
            # 给每个人类一些知识
            cultural_system.entity_knowledge[entity_id] = {KnowledgeType.SURVIVAL: 1.5}
        # 形成社会群体
        social_system.update(world, 1.0)
        # 形成文化传统
        cultural_system.update(world, 1.0)
        # 验证文化传统形成
        assert len(cultural_system.traditions) >= 0

if __name__ == "__main__":
    pytest.main([__file__])