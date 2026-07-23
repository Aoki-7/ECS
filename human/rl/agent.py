#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q学习智能体：用于人类行为决策
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
import random
import pickle
import os

class QLearningAgent:
    """Q学习智能体"""

    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.1,
                 discount_factor: float = 0.95, exploration_rate: float = 0.1,
                 exploration_decay: float = 0.995, min_exploration: float = 0.01):
        """
        初始化Q学习智能体
        Args:
            state_size: 状态空间大小
            action_size: 动作空间大小
            learning_rate: 学习率
            discount_factor: 折扣因子
            exploration_rate: 探索率
            exploration_decay: 探索率衰减
            min_exploration: 最小探索率
        """
        self.state_size = state_size
        self.action_size = action_size
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.epsilon_decay = exploration_decay
        self.min_epsilon = min_exploration

        # Q表：使用字典存储，键是状态的哈希，值是动作价值数组
        self.q_table: Dict[int, np.ndarray] = {}

        # 训练统计
        self.total_steps = 0
        self.total_reward = 0.0

    def get_state_key(self, state: np.ndarray) -> int:
        """将连续状态离散化为键"""
        # 简单的离散化：将每个维度分成10个区间
        discretized = tuple(np.round(state * 10).astype(int))
        return hash(discretized)

    def choose_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        选择动作：ε-贪婪策略
        Args:
            state: 当前状态
            training: 是否训练模式（训练模式使用探索，测试模式使用最优动作）
        Returns:
            动作索引
        """
        state_key = self.get_state_key(state)

        # 如果状态不在Q表中，初始化为0
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)

        # ε-贪婪策略
        if training and random.random() < self.epsilon:
            # 探索：随机选择动作
            return random.randint(0, self.action_size - 1)
        else:
            # 利用：选择最优动作
            return np.argmax(self.q_table[state_key])

    def learn(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """
        更新Q表
        Args:
            state: 当前状态
            action: 执行的动作
            reward: 获得的奖励
            next_state: 下一个状态
            done: 是否结束
        """
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)

        # 初始化Q值
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_size)

        # Q学习更新规则
        current_q = self.q_table[state_key][action]
        max_next_q = np.max(self.q_table[next_state_key])
        target_q = reward + (0 if done else self.gamma * max_next_q)
        new_q = current_q + self.lr * (target_q - current_q)
        self.q_table[state_key][action] = new_q

        # 更新统计
        self.total_steps += 1
        self.total_reward += reward

        # 衰减探索率
        if done:
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def save(self, path: str):
        """保存Q表"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'epsilon': self.epsilon,
                'total_steps': self.total_steps,
                'total_reward': self.total_reward
            }, f)

    def load(self, path: str):
        """加载Q表"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.q_table = data['q_table']
                self.epsilon = data['epsilon']
                self.total_steps = data['total_steps']
                self.total_reward = data['total_reward']

    def get_stats(self) -> Dict[str, float]:
        """获取训练统计"""
        return {
            'total_steps': self.total_steps,
            'total_reward': self.total_reward,
            'avg_reward': self.total_reward / max(self.total_steps, 1),
            'epsilon': self.epsilon
        }