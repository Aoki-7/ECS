#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层强化学习意图系统 v2.0：结合动作元件和动作规划，自发组合复杂动作
支持自动学习动作组合，无需人工规划
支持多智能体协作
"""
import logging
import numpy as np
from typing import Dict, Optional, List, Tuple
from core.system import System
from core.world import World
from human.components.cognitive.intent_component import IntentComponent, IntentType
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from human.rl.environment import ECSEnvironment
from human.rl.agent import QLearningAgent
from human.rl.action_primitives import ActionPrimitive, ActionSequence, ActionPrimitiveType, get_action_primitive

logger = logging.getLogger(__name__)

class HierarchicalRLIntentSystem(System):
    """分层强化学习意图系统：高层选择目标，低层学习动作组合"""
    tick_interval = 1  # 每1帧执行一次

    def __init__(self, model_path: Optional[str] = None, training: bool = True):
        """
        初始化分层RL意图系统
        Args:
            model_path: 预训练模型路径
            training: 是否训练模式
        """
        self.training = training
        self.model_path = model_path or "models/hierarchical_rl_agent.pkl"
        # 高层智能体：选择目标
        self.high_level_agent = QLearningAgent(state_size=40, action_size=10)  # 10种目标类型
        # 低层智能体：学习动作组合（状态+目标 -> 动作元件）
        self.low_level_agent = QLearningAgent(state_size=50, action_size=len(ActionPrimitiveType))
        # 多智能体协作智能体：学习协作策略
        self.cooperation_agent = QLearningAgent(state_size=60, action_size=5)  # 5种协作模式
        if not training:
            self.high_level_agent.load(self.model_path + ".high")
            self.low_level_agent.load(self.model_path + ".low")
            self.cooperation_agent.load(self.model_path + ".coop")
        self.step_count = 0
        self.environments: Dict[int, ECSEnvironment] = {}
        self.current_goals: Dict[int, str] = {}  # 实体ID -> 目标类型
        self.current_sequences: Dict[int, List[ActionPrimitive]] = {}  # 实体ID -> 动作序列
        self.current_primitive_idx: Dict[int, int] = {}  # 实体ID -> 当前动作索引
        self.cooperation_partners: Dict[int, List[int]] = {}  # 实体ID -> 协作伙伴列表

    def update(self, world: World, dt: float):
        """更新分层意图系统"""
        self.step_count += 1

        # 每1000步保存一次模型
        if self.training and self.step_count % 1000 == 0:
            self.high_level_agent.save(self.model_path + ".high")
            self.low_level_agent.save(self.model_path + ".low")
            self.cooperation_agent.save(self.model_path + ".coop")
            high_stats = self.high_level_agent.get_stats()
            low_stats = self.low_level_agent.get_stats()
            coop_stats = self.cooperation_agent.get_stats()
            logger.info(f"[HierarchicalRL] 保存模型: 高层={high_stats}, 低层={low_stats}, 协作={coop_stats}")

        # 获取所有人类实体
        human_entities = [e.id for e, _ in world.get_components(HumanComponent)]

        # 遍历所有有生理需求和意图组件的实体
        for e, (needs, intent) in world.get_components(PhysiologyNeedsComponent, IntentComponent):
            entity_id = e.id

            # 获取或创建环境
            if entity_id not in self.environments:
                self.environments[entity_id] = ECSEnvironment(world, entity_id)
            env = self.environments[entity_id]

            # 获取当前状态
            state = env.get_state()

            # 1. 多智能体协作决策：选择协作伙伴
            coop_action = None

            # 初始化新实体的RL状态（避免KeyError）
            if entity_id not in self.current_goals:
                self.current_goals[entity_id] = "survive"
            if entity_id not in self.current_sequences:
                self.current_sequences[entity_id] = []
            if entity_id not in self.current_primitive_idx:
                self.current_primitive_idx[entity_id] = 0
            if entity_id not in self.cooperation_partners:
                self.cooperation_partners[entity_id] = []

            if len(self.cooperation_partners[entity_id]) == 0:
                coop_state = self._get_cooperation_state(world, entity_id, state)
                coop_action = self.cooperation_agent.choose_action(coop_state, training=self.training)
                # 根据协作动作选择伙伴
                partners = self._select_cooperation_partners(world, entity_id, human_entities, coop_action)
                self.cooperation_partners[entity_id] = partners

            # 2. 高层决策：选择目标
            goal_idx = None
            if entity_id not in self.current_goals:
                goal_state = np.concatenate([state, [len(self.cooperation_partners.get(entity_id, [])) / 5.0]])
                goal_idx = self.high_level_agent.choose_action(goal_state, training=self.training)
                goal_type = ["survive", "socialize", "explore", "build", "work", "flee", "idle", "trade", "cooperate", "learn"][goal_idx]
                self.current_goals[entity_id] = goal_type
                self.current_sequences[entity_id] = []
                self.current_primitive_idx[entity_id] = 0

            current_goal = self.current_goals[entity_id]
            primitive_idx = None
            goal_idx = None

            # 3. 低层决策：学习动作组合
            if self.current_primitive_idx[entity_id] >= len(self.current_sequences[entity_id]):
                # 生成新的动作序列
                low_state = np.concatenate([state, [hash(current_goal) % 100 / 100.0]])
                primitive_idx = self.low_level_agent.choose_action(low_state, training=self.training)
                primitive_type = list(ActionPrimitiveType)[primitive_idx]

                # 根据目标和动作类型生成动作序列
                sequence = self._generate_action_sequence(world, entity_id, current_goal, primitive_type)
                self.current_sequences[entity_id] = sequence
                self.current_primitive_idx[entity_id] = 0

            # 4. 执行当前动作
            if self.current_primitive_idx[entity_id] < len(self.current_sequences[entity_id]):
                current_primitive = self.current_sequences[entity_id][self.current_primitive_idx[entity_id]]
                success = current_primitive.execute(world, entity_id)

                if success:
                    # 前进到下一个动作
                    self.current_primitive_idx[entity_id] += 1
                else:
                    # 动作失败，重新规划
                    self.current_sequences[entity_id] = []
                    self.current_primitive_idx[entity_id] = 0

                # 5. 更新意图组件（用于可视化）
                intent.intent = self._map_primitive_to_intent(current_primitive.type)
                intent.priority = 1.0
                # 设置当前动作，用于行为可视化
                intent.current_action = current_primitive
                intent.cooperation_partners = self.cooperation_partners.get(entity_id, [])
                intent.goal_type = current_goal

                # 6. 学习
                if self.training:
                    # 计算奖励
                    reward = self._calculate_reward(world, entity_id, current_goal, current_primitive, success)
                    # 更新低层智能体
                    low_state = np.concatenate([state, [hash(current_goal) % 100 / 100.0]])
                    next_state = env.get_state()
                    next_low_state = np.concatenate([next_state, [hash(current_goal) % 100 / 100.0]])
                    done = self.current_primitive_idx[entity_id] >= len(self.current_sequences[entity_id])
                    self.low_level_agent.learn(low_state, primitive_idx, reward, next_low_state, done)
                    # 更新高层智能体
                    if done and goal_idx is not None:
                        goal_reward = reward if success else -1.0
                        goal_state = np.concatenate([state, [len(self.cooperation_partners.get(entity_id, [])) / 5.0]])
                        next_goal_state = np.concatenate([next_state, [len(self.cooperation_partners.get(entity_id, [])) / 5.0]])
                        self.high_level_agent.learn(goal_state, goal_idx, goal_reward, next_goal_state, False)
                    # 更新协作智能体
                    if coop_action is not None:
                        coop_state = self._get_cooperation_state(world, entity_id, state)
                        coop_reward = self._calculate_cooperation_reward(world, entity_id, success)
                        next_coop_state = self._get_cooperation_state(world, entity_id, next_state)
                        self.cooperation_agent.learn(coop_state, coop_action, coop_reward, next_coop_state, False)

    def _get_cooperation_state(self, world: World, entity_id: int, state: np.ndarray) -> np.ndarray:
        """获取协作状态"""
        # 附近的人类数量
        nearby_humans = self._get_nearby_humans(world, entity_id, radius=10.0)
        # 协作伙伴数量
        num_partners = len(self.cooperation_partners.get(entity_id, []))
        # 组合状态
        coop_state = np.concatenate([state, [len(nearby_humans) / 10.0, num_partners / 5.0]])
        return coop_state

    def _get_nearby_humans(self, world: World, entity_id: int, radius: float = 10.0) -> List[int]:
        """获取附近的人类实体"""
        pos = world.get_component(entity_id, SpaceComponent)
        if not pos:
            return []
        nearby = []
        for e, (human, human_pos) in world.get_components(HumanComponent, SpaceComponent):
            if e.id == entity_id:
                continue
            distance = ((pos.x - human_pos.x)**2 + (pos.y - human_pos.y)**2)**0.5
            if distance <= radius:
                nearby.append(e.id)
        return nearby

    def _select_cooperation_partners(self, world: World, entity_id: int, human_entities: List[int], coop_action: int) -> List[int]:
        """选择协作伙伴"""
        nearby = self._get_nearby_humans(world, entity_id, radius=10.0)
        if coop_action == 0:  # 独自工作
            return []
        elif coop_action == 1:  # 小团队合作（2-3人）
            return nearby[:2]
        elif coop_action == 2:  # 大团队合作（4-5人）
            return nearby[:4]
        elif coop_action == 3:  # 与最强的人合作
            # 简化：选择库存最多的人
            return nearby[:1]
        elif coop_action == 4:  # 与最弱的人合作（教学）
            # 简化：选择库存最少的人
            return nearby[-1:]
        return []

    def _generate_action_sequence(self, world: World, entity_id: int, goal: str, primitive_type: ActionPrimitiveType) -> List[ActionPrimitive]:
        """根据目标和动作类型生成动作序列"""
        sequence = []

        if goal == "survive":
            if primitive_type == ActionPrimitiveType.CONSUME:
                # 寻找食物/水 -> 移动 -> 抓取 -> 消耗
                nearest_food = self._find_nearest_resource(world, entity_id, "food")
                if nearest_food:
                    food_pos = world.get_component(nearest_food, SpaceComponent)
                    sequence.append(get_action_primitive(ActionPrimitiveType.MOVE_TO, x=food_pos.x, y=food_pos.y))
                    sequence.append(get_action_primitive(ActionPrimitiveType.GRAB, target_entity=nearest_food))
                    sequence.append(get_action_primitive(ActionPrimitiveType.CONSUME, item_id=hash(nearest_food)))
            elif primitive_type == ActionPrimitiveType.REST:
                sequence.append(get_action_primitive(ActionPrimitiveType.REST, duration=10.0))

        elif goal == "socialize":
            # 寻找附近的人类 -> 移动 -> 社交
            nearby_humans = self._get_nearby_humans(world, entity_id, radius=20.0)
            if nearby_humans:
                target = nearby_humans[0]
                target_pos = world.get_component(target, SpaceComponent)
                if target_pos is not None:
                    sequence.append(get_action_primitive(ActionPrimitiveType.MOVE_TO, x=target_pos.x, y=target_pos.y))
                    sequence.append(get_action_primitive(ActionPrimitiveType.SOCIALIZE, target_entity=target))

        elif goal == "work":
            # 寻找资源 -> 移动 -> 采集
            nearest_resource = self._find_nearest_resource(world, entity_id, "any")
            if nearest_resource:
                resource_pos = world.get_component(nearest_resource, SpaceComponent)
                if resource_pos is not None:
                    sequence.append(get_action_primitive(ActionPrimitiveType.MOVE_TO, x=resource_pos.x, y=resource_pos.y))
                    sequence.append(get_action_primitive(ActionPrimitiveType.GATHER, target_entity=nearest_resource))

        elif goal == "cooperate":
            # 与协作伙伴一起工作
            partners = self.cooperation_partners.get(entity_id, [])
            if partners:
                target = partners[0]
                target_pos = world.get_component(target, SpaceComponent)
                if target_pos is not None:
                    sequence.append(get_action_primitive(ActionPrimitiveType.MOVE_TO, x=target_pos.x, y=target_pos.y))
                    sequence.append(get_action_primitive(ActionPrimitiveType.COOPERATE, target_entity=target, task="gather"))

        elif goal == "flee":
            sequence.append(get_action_primitive(ActionPrimitiveType.FLEE))

        elif goal == "build":
            # 寻找建造地点 -> 移动 -> 建造
            import random
            pos = world.get_component(entity_id, SpaceComponent)
            if pos:
                build_x = pos.x + random.uniform(-5, 5)
                build_y = pos.y + random.uniform(-5, 5)
                sequence.append(get_action_primitive(ActionPrimitiveType.MOVE_TO, x=build_x, y=build_y))
                sequence.append(get_action_primitive(ActionPrimitiveType.BUILD, structure_type="house", position=(build_x, build_y)))

        # 如果没有生成动作，默认休息
        if len(sequence) == 0:
            sequence.append(get_action_primitive(ActionPrimitiveType.REST, duration=5.0))

        return sequence

    def _find_nearest_resource(self, world: World, entity_id: int, resource_type: str) -> Optional[int]:
        """查找最近的资源实体"""
        from resource.components.resource_component import ResourceComponent
        from space.space_component import SpaceComponent
        pos = world.get_component(entity_id, SpaceComponent)
        if not pos:
            return None
        nearest_entity = None
        min_distance = float('inf')
        for e, (resource, res_pos) in world.get_components(ResourceComponent, SpaceComponent):
            if resource_type != "any" and resource.resource_type != resource_type:
                continue
            distance = ((pos.x - res_pos.x)**2 + (pos.y - res_pos.y)**2)**0.5
            if distance < min_distance:
                min_distance = distance
                nearest_entity = e.id
        return nearest_entity

    def _map_primitive_to_intent(self, primitive_type: ActionPrimitiveType) -> IntentType:
        """将动作元件映射到意图类型（用于可视化）"""
        mapping = {
            ActionPrimitiveType.MOVE_TO: IntentType.EXPLORE,
            ActionPrimitiveType.GRAB: IntentType.COLLECT,
            ActionPrimitiveType.CONSUME: IntentType.EAT,
            ActionPrimitiveType.REST: IntentType.SLEEP,
            ActionPrimitiveType.SOCIALIZE: IntentType.SOCIALIZE,
            ActionPrimitiveType.FLEE: IntentType.FLEE,
            ActionPrimitiveType.BUILD: IntentType.BUILD,
            ActionPrimitiveType.CRAFT: IntentType.CRAFT,
            ActionPrimitiveType.GATHER: IntentType.COLLECT,
            ActionPrimitiveType.EXPLORE: IntentType.EXPLORE,
            ActionPrimitiveType.INVESTIGATE: IntentType.INVESTIGATE,
            ActionPrimitiveType.COOPERATE: IntentType.SOCIALIZE,
            ActionPrimitiveType.TEACH: IntentType.SOCIALIZE,
        }
        return mapping.get(primitive_type, IntentType.IDLE)

    def _calculate_reward(self, world: World, entity_id: int, goal: str, primitive: ActionPrimitive, success: bool) -> float:
        """计算奖励函数"""
        from biology.components.physiology_needs_component import PhysiologyNeedsComponent
        needs = world.get_component(entity_id, PhysiologyNeedsComponent)
        if not needs:
            return 0.0

        reward = 0.0

        # 1. 动作成功奖励
        if success:
            reward += 0.5

        # 2. 目标相关奖励
        if goal == "survive":
            if primitive.type == ActionPrimitiveType.CONSUME and needs.hunger < 30:
                reward += 1.0
            elif primitive.type == ActionPrimitiveType.CONSUME and needs.thirst < 30:
                reward += 1.0
            elif primitive.type == ActionPrimitiveType.REST and needs.energy > 80:
                reward += 1.0
        elif goal == "socialize":
            if primitive.type == ActionPrimitiveType.SOCIALIZE and needs.social > 80:
                reward += 1.0
        elif goal == "cooperate":
            if primitive.type == ActionPrimitiveType.COOPERATE:
                reward += 1.5  # 协作奖励更高
        elif goal == "work":
            if primitive.type == ActionPrimitiveType.GATHER:
                reward += 1.0
        elif goal == "flee":
            if primitive.type == ActionPrimitiveType.FLEE:
                reward += 1.0

        # 3. 需求惩罚
        if needs.hunger > 70 and goal != "survive":
            reward -= 0.5
        if needs.thirst > 70 and goal != "survive":
            reward -= 0.5
        if needs.energy < 20 and goal != "survive":
            reward -= 0.5

        return reward

    def _calculate_cooperation_reward(self, world: World, entity_id: int, success: bool) -> float:
        """计算协作奖励"""
        partners = self.cooperation_partners.get(entity_id, [])
        if not partners:
            return 0.0
        # 协作伙伴越多，奖励越高
        reward = len(partners) * 0.5
        if success:
            reward += 1.0
        return reward

    def get_stats(self) -> Dict[str, float]:
        """获取智能体统计"""
        high_stats = self.high_level_agent.get_stats()
        low_stats = self.low_level_agent.get_stats()
        coop_stats = self.cooperation_agent.get_stats()
        return {
            "high_level_avg_reward": high_stats["avg_reward"],
            "low_level_avg_reward": low_stats["avg_reward"],
            "cooperation_avg_reward": coop_stats["avg_reward"],
            "high_level_epsilon": high_stats["epsilon"],
            "low_level_epsilon": low_stats["epsilon"],
            "cooperation_epsilon": coop_stats["epsilon"],
        }
