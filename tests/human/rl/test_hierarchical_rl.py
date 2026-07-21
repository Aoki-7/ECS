#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层RL系统测试
"""
import pytest
import numpy as np
from core.world import World
from human.rl.action_primitives import ActionPrimitive, ActionSequence, ActionPrimitiveType, get_action_primitive
from human.rl.action_planner import ActionPlanner, Goal
from human.rl.hierarchical_rl_intent_system import HierarchicalRLIntentSystem
from human.components.cognitive.intent_component import IntentComponent, IntentType
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from core.components.world_config_component import WorldConfigComponent

class TestActionPrimitives:
    """动作元件测试"""
    def test_move_to_action(self):
        """测试移动动作"""
        world = World()
        entity_id = world.create_entity()
        world.add_component(entity_id, SpaceComponent(x=0, y=0))
        action = get_action_primitive(ActionPrimitiveType.MOVE_TO, x=10, y=10)
        assert action is not None
        assert action.type == ActionPrimitiveType.MOVE_TO
        success = action.execute(world, entity_id)
        assert success
        pos = world.get_component(entity_id, SpaceComponent)
        assert pos.x == 10 and pos.y == 10

    def test_rest_action(self):
        """测试休息动作"""
        world = World()
        entity_id = world.create_entity()
        needs = PhysiologyNeedsComponent(energy=50)
        world.add_component(entity_id, needs)
        action = get_action_primitive(ActionPrimitiveType.REST, duration=5.0)
        assert action is not None
        success = action.execute(world, entity_id)
        assert success
        assert needs.energy > 50

class TestActionPlanner:
    """动作规划器测试"""
    def test_plan_survive(self):
        """测试生存目标规划"""
        world = World()
        entity_id = world.create_entity()
        world.add_component(entity_id, PhysiologyNeedsComponent(hunger=80, thirst=30, energy=50))
        world.add_component(entity_id, SpaceComponent(x=0, y=0))
        planner = ActionPlanner(world, entity_id)
        goal = Goal(type="survive")
        sequence = planner.plan(goal)
        assert sequence is not None
        assert len(sequence.primitives) > 0

    def test_plan_socialize(self):
        """测试社交目标规划"""
        world = World()
        entity_id = world.create_entity()
        world.add_component(entity_id, SpaceComponent(x=0, y=0))
        planner = ActionPlanner(world, entity_id)
        goal = Goal(type="socialize")
        sequence = planner.plan(goal)
        assert sequence is not None

class TestHierarchicalRLSystem:
    """分层RL系统测试"""
    def test_hierarchical_rl_system(self):
        """测试分层RL系统"""
        world = World()
        # 添加配置，启用RL意图系统
        world_entity = world.get_world_entity()
        world.add_component(world_entity, WorldConfigComponent(use_rl_intent=True, rl_training=True))
        # 创建人类实体
        entity_id = world.create_entity()
        world.add_component(entity_id, PhysiologyNeedsComponent(hunger=80, thirst=30, energy=50))
        world.add_component(entity_id, IntentComponent())
        world.add_component(entity_id, SpaceComponent(x=0, y=0))
        world.add_component(entity_id, MemoryComponent())
        # 创建分层RL系统
        rl_system = HierarchicalRLIntentSystem(training=True)
        rl_system.update(world, 1.0)
        # 验证意图已更新
        intent = world.get_component(entity_id, IntentComponent)
        assert intent.intent is not None

if __name__ == "__main__":
    pytest.main([__file__])
