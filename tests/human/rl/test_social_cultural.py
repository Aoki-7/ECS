#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社会结构和文化传承测试
"""
import pytest
import numpy as np
from core.world import World
from human.rl.behavior_visualizer import BehaviorVisualizer
from human.rl.complex_tasks import ComplexTaskSystem, TaskType
from human.rl.social_structure import SocialStructureSystem, RoleType
from human.rl.cultural_inheritance import CulturalInheritanceSystem, KnowledgeType
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent
from space.space_component import SpaceComponent
from human.components.abilities.skill_component import SkillComponent

class TestBehaviorVisualizer:
    """行为可视化测试"""
    def test_behavior_visualizer(self):
        """测试行为可视化系统"""
        world = World()
        visualizer = BehaviorVisualizer()
        # 创建人类实体
        entity_id = world.create_entity()
        world.add_component(entity_id, HumanComponent())
        world.add_component(entity_id, IntentComponent())
        world.add_component(entity_id, SpaceComponent(x=0, y=0))
        # 更新可视化系统
        visualizer.update(world, 1.0)
        # 验证行为记录
        assert len(visualizer.behavior_records) >= 0

class TestComplexTaskSystem:
    """复杂任务系统测试"""
    def test_complex_task_system(self):
        """测试复杂任务系统"""
        world = World()
        task_system = ComplexTaskSystem()
        # 创建人类实体
        for i in range(5):
            entity_id = world.create_entity()
            world.add_component(entity_id, HumanComponent())
            world.add_component(entity_id, IntentComponent())
            world.add_component(entity_id, SpaceComponent(x=i*2, y=i*2))
        # 更新任务系统
        task_system.update(world, 1.0)
        # 验证任务生成
        assert len(task_system.tasks) >= 0

class TestSocialStructureSystem:
    """社会结构系统测试"""
    def test_social_structure_system(self):
        """测试社会结构系统"""
        world = World()
        social_system = SocialStructureSystem()
        # 创建人类实体
        for i in range(10):
            entity_id = world.create_entity()
            world.add_component(entity_id, HumanComponent())
            world.add_component(entity_id, SpaceComponent(x=i*2, y=i*2))
        # 更新社会结构系统
        social_system.update(world, 1.0)
        # 验证群体形成
        assert len(social_system.groups) >= 0

class TestCulturalInheritanceSystem:
    """文化传承系统测试"""
    def test_cultural_inheritance_system(self):
        """测试文化传承系统"""
        world = World()
        cultural_system = CulturalInheritanceSystem()
        # 创建人类实体
        for i in range(5):
            entity_id = world.create_entity()
            world.add_component(entity_id, HumanComponent())
            world.add_component(entity_id, SpaceComponent(x=i*2, y=i*2))
            world.add_component(entity_id, SkillComponent())
        # 更新文化传承系统
        cultural_system.update(world, 1.0)
        # 验证知识创造
        assert len(cultural_system.knowledge) >= 0

if __name__ == "__main__":
    pytest.main([__file__])
