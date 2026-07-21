#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RL意图系统演示：训练Q学习智能体学习人类行为
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from core.world import World
from human.rl import RLIntentSystem
from human.components.cognitive.intent_component import IntentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from core.components.world_config_component import WorldConfigComponent

def train_rl_agent(num_episodes=100, steps_per_episode=1000):
    """训练RL智能体"""
    print("开始训练RL意图智能体...")
    print(f"训练回合数: {num_episodes}, 每回合步数: {steps_per_episode}")

    # 创建世界
    world = World()
    world_entity = world.get_world_entity()
    world.add_component(world_entity, WorldConfigComponent(use_rl_intent=True, rl_training=True))

    # 创建人类实体
    entity_id = world.create_entity()
    world.add_component(entity_id, PhysiologyNeedsComponent(hunger=50, thirst=50, energy=80, health=100))
    world.add_component(entity_id, IntentComponent())
    world.add_component(entity_id, SpaceComponent(x=0, y=0))
    world.add_component(entity_id, MemoryComponent())

    # 创建RL系统
    rl_system = RLIntentSystem(training=True)

    # 训练循环
    for episode in range(num_episodes):
        # 重置需求
        needs = world.get_component(entity_id, PhysiologyNeedsComponent)
        needs.hunger = 50
        needs.thirst = 50
        needs.energy = 80
        needs.health = 100

        total_reward = 0.0
        for step in range(steps_per_episode):
            # 更新RL系统
            rl_system.update(world, 1.0)

            # 模拟需求变化
            needs.hunger = min(100, needs.hunger + 0.1)
            needs.thirst = min(100, needs.thirst + 0.2)
            needs.energy = max(0, needs.energy - 0.05)

            # 如果需求满足，获得奖励
            if needs.hunger < 30:
                needs.hunger = 50  # 吃了东西
                total_reward += 1.0
            if needs.thirst < 30:
                needs.thirst = 50  # 喝了水
                total_reward += 1.0
            if needs.energy > 80:
                needs.energy = 80  # 睡了觉
                total_reward += 1.0

        # 打印训练进度
        if episode % 10 == 0:
            stats = rl_system.get_stats()
            print(f"回合 {episode}/{num_episodes}: 平均奖励 = {stats['avg_reward']:.2f}, 探索率 = {stats['epsilon']:.2f}")

    # 保存模型
    rl_system.global_agent.save("models/rl_intent_agent.pkl")
    print("训练完成！模型已保存到 models/rl_intent_agent.pkl")

def test_rl_agent():
    """测试训练好的RL智能体"""
    print("\n测试训练好的RL智能体...")

    # 创建世界
    world = World()
    world_entity = world.get_world_entity()
    world.add_component(world_entity, WorldConfigComponent(use_rl_intent=True, rl_training=False))

    # 创建人类实体
    entity_id = world.create_entity()
    world.add_component(entity_id, PhysiologyNeedsComponent(hunger=80, thirst=30, energy=50, health=100))
    world.add_component(entity_id, IntentComponent())
    world.add_component(entity_id, SpaceComponent(x=0, y=0))
    world.add_component(entity_id, MemoryComponent())
    # 添加视觉组件，支持感知
    from human.components.perception.vision_component import VisionComponent
    world.add_component(entity_id, VisionComponent())

    # 创建RL系统（推理模式）
    rl_system = RLIntentSystem(training=False)
    rl_system.global_agent.load("models/rl_intent_agent.pkl")

    # 测试几步
    for step in range(10):
        rl_system.update(world, 1.0)
        intent = world.get_component(entity_id, IntentComponent)
        needs = world.get_component(entity_id, PhysiologyNeedsComponent)
        # 获取环境状态
        env = rl_system.environments[entity_id.id]
        state = env.get_state()
        print(f"步 {step}:")
        print(f"  需求 = (饥饿:{needs.hunger:.0f}, 口渴:{needs.thirst:.0f}, 能量:{needs.energy:.0f})")
        print(f"  环境状态 = 位置({state[5]:.2f},{state[6]:.2f}), 库存(食物:{state[7]:.2f}, 水:{state[8]:.2f}), 最近食物距离:{state[10]:.2f}")
        print(f"  社交信息 = 附近人类:{state[25]:.2f}, 朋友数量:{state[26]:.2f}, 社交需求:{state[27]:.2f}")
        print(f"  选择的意图 = {intent.intent.name}")
        print()

if __name__ == "__main__":
    # 训练智能体
    train_rl_agent(num_episodes=50, steps_per_episode=100)
    # 测试智能体
    test_rl_agent()
