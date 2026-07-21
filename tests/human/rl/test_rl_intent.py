#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RL意图系统测试
"""
import pytest
import numpy as np
from core.world import World
from human.rl import ECSEnvironment, QLearningAgent, RLIntentSystem
from human.components.cognitive.intent_component import IntentComponent, IntentType
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from core.components.world_config_component import WorldConfigComponent

class TestQLearningAgent:
    """Q学习智能体测试"""
    def test_agent_init(self):
        """测试智能体初始化"""
        agent = QLearningAgent(state_size=40, action_size=10)
        assert agent.state_size == 40
        assert agent.action_size == 10
        assert agent.epsilon == 0.1

    def test_choose_action(self):
        """测试动作选择"""
        agent = QLearningAgent(state_size=40, action_size=10)
        state = np.random.rand(40)
        action = agent.choose_action(state, training=False)
        assert 0 <= action < 10

    def test_learn(self):
        """测试学习功能"""
        agent = QLearningAgent(state_size=40, action_size=10)
        state = np.random.rand(40)
        next_state = np.random.rand(40)
        agent.learn(state, 0, 1.0, next_state, False)
        # 验证Q表已更新
        state_key = agent.get_state_key(state)
        assert state_key in agent.q_table
        assert agent.q_table[state_key][0] > 0

class TestECSEnvironment:
    """ECS环境测试"""
    def test_environment_init(self):
        """测试环境初始化"""
        world = World()
        entity_id = world.create_entity()
        world.add_component(entity_id, PhysiologyNeedsComponent())
        world.add_component(entity_id, SpaceComponent(x=0, y=0))
        env = ECSEnvironment(world, entity_id)
        assert env.entity_id == entity_id
        assert len(env.actions) == 10

    def test_get_state(self):
        """测试获取状态"""
        world = World()
        entity_id = world.create_entity()
        needs = PhysiologyNeedsComponent(hunger=50, thirst=50, energy=80)
        world.add_component(entity_id, needs)
        world.add_component(entity_id, SpaceComponent(x=10, y=10))
        env = ECSEnvironment(world, entity_id)
        state = env.get_state()
        assert len(state) == env.state_space_size
        assert state[0] == 0.5  # hunger
        assert state[1] == 0.5  # thirst
        assert state[2] == 0.8  # energy

class TestRLIntentSystem:
    """RL意图系统测试"""
    def test_rl_intent_system(self):
        """测试RL意图系统"""
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
        # 创建RL系统
        rl_system = RLIntentSystem(training=True)
        rl_system.update(world, 1.0)
        # 验证意图已更新
        intent = world.get_component(entity_id, IntentComponent)
        assert intent.intent in [IntentType.EAT, IntentType.DRINK, IntentType.SLEEP, IntentType.IDLE, IntentType.EXPLORE, IntentType.WORK, IntentType.FLEE]

if __name__ == "__main__":
    pytest.main([__file__])
