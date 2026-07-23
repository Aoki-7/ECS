#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强化学习意图系统：使用Q学习替代规则驱动的意图决策
"""
import logging
from typing import Dict, Optional
from core.system import System
from core.world import World
from human.components.cognitive.intent_component import IntentComponent, IntentType
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.rl.environment import ECSEnvironment
from human.rl.agent import QLearningAgent

logger = logging.getLogger(__name__)

class RLIntentSystem(System):
    """强化学习意图系统"""
    tick_interval = 1  # 每1帧执行一次

    def __init__(self, model_path: Optional[str] = None, training: bool = True):
        """
        初始化RL意图系统
        Args:
            model_path: 预训练模型路径，如果为None则从头开始训练
            training: 是否训练模式，False则使用预训练模型进行推理
        """
        self.training = training
        self.agents: Dict[int, QLearningAgent] = {}  # 实体ID -> 智能体
        self.environments: Dict[int, ECSEnvironment] = {}  # 实体ID -> 环境
        self.model_path = model_path or "models/rl_intent_agent.pkl"
        self.global_agent = QLearningAgent(state_size=40, action_size=10)  # 全局共享智能体，支持更多状态和动作
        if not training:
            self.global_agent.load(self.model_path)
        self.step_count = 0

    def update(self, world: World, dt: float):
        """更新意图系统"""
        self.step_count += 1

        # 每1000步保存一次模型
        if self.training and self.step_count % 1000 == 0:
            self.global_agent.save(self.model_path)
            stats = self.global_agent.get_stats()
            logger.info(f"[RLIntentSystem] 保存模型: {stats}")

        # 遍历所有有生理需求和意图组件的实体
        for e, (needs, intent) in world.get_components(PhysiologyNeedsComponent, IntentComponent):
            entity_id = e.id

            # 获取或创建环境和智能体
            if entity_id not in self.environments:
                self.environments[entity_id] = ECSEnvironment(world, entity_id)
            env = self.environments[entity_id]

            # 获取当前状态
            state = env.get_state()

            # 选择动作（意图）
            action_idx = self.global_agent.choose_action(state, training=self.training)
            action = env.actions[action_idx]

            # 更新意图组件
            intent.intent = action
            intent.priority = 1.0  # RL系统不使用优先级，由Q值决定

            # 如果是训练模式，学习
            if self.training:
                # 模拟执行动作，获取奖励和下一个状态
                next_state, reward, done, info = env.step(action_idx)
                # 学习
                self.global_agent.learn(state, action_idx, reward, next_state, done)

                # 记录到记忆
                memory = world.get_component(entity_id, MemoryComponent)
                if memory:
                    action_name = action.name.lower()
                    if reward > 0:
                        memory.recent_successes[action_name] = memory.recent_successes.get(action_name, 0) + 1

    def get_stats(self) -> Dict[str, float]:
        """获取智能体统计"""
        return self.global_agent.get_stats()