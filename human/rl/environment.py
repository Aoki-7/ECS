#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECS世界强化学习环境封装（v2.0）
将ECS世界转换为符合Gym风格的强化学习环境，扩展了更多环境信息
"""
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from core.world import World
from human.components.cognitive.intent_component import IntentType
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from resource.components.resource_component import ResourceComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.perception.vision_component import VisionComponent
from human.components.basic.human_component import HumanComponent
from civilization.settlement.components.settlement_component import SettlementComponent
from biology.organisms.animal.components.animal_component import AnimalComponent

class ECSEnvironment:
    """ECS世界强化学习环境 v2.0，支持更多环境信息"""

    def __init__(self, world: World, entity_id: int):
        """
        初始化环境
        Args:
            world: ECS世界实例
            entity_id: 人类实体ID
        """
        self.world = world
        self.entity_id = entity_id

        # 动作空间：所有可能的意图
        self.actions = [
            IntentType.IDLE,
            IntentType.EAT,
            IntentType.DRINK,
            IntentType.SLEEP,
            IntentType.SOCIALIZE,
            IntentType.EXPLORE,
            IntentType.WORK,  # 工作（采集/制作）
            IntentType.FLEE,  # 逃跑（如果有危险）
            IntentType.BUILD,  # 建造
            IntentType.TRADE,  # 交易
        ]
        self.action_space_size = len(self.actions)

        # 状态空间：生理需求 + 位置 + 周围环境 + 库存 + 感知信息 + 天气 + 社交 + 危险
        self.state_space_size = 40  # 扩展后的状态空间大小

    def get_state(self) -> np.ndarray:
        """获取当前状态向量，包含更多环境信息"""
        state = []

        # 1. 生理需求（0-100归一化）
        needs = self.world.get_component(self.entity_id, PhysiologyNeedsComponent)
        if needs:
            state.extend([
                needs.hunger / 100.0,
                needs.thirst / 100.0,
                needs.energy / 100.0,
                needs.social / 100.0,
                needs.health / 100.0,
            ])
        else:
            state.extend([0.0] * 5)

        # 2. 位置（归一化到0-1）
        pos = self.world.get_component(self.entity_id, SpaceComponent)
        if pos:
            # 假设世界大小是100x100，动态获取
            state.extend([
                pos.x / 100.0,
                pos.y / 100.0,
            ])
        else:
            state.extend([0.0, 0.0])

        # 3. 库存资源（归一化）
        inventory = self.world.get_component(self.entity_id, InventoryComponent)
        if inventory:
            # 计算食物、水、工具数量
            food_count = 0.0
            water_count = 0.0
            tool_count = 0.0
            for item_key, amount in inventory.items.items():
                # 这里简化处理，实际应该根据物品类型分类
                if "food" in str(item_key):
                    food_count += amount
                elif "water" in str(item_key):
                    water_count += amount
                else:
                    tool_count += amount
            state.extend([
                min(food_count / 100.0, 1.0),  # 归一化到0-1
                min(water_count / 100.0, 1.0),
                min(tool_count / 10.0, 1.0),
            ])
        else:
            state.extend([0.0] * 3)

        # 4. 周围环境：最近的资源距离（归一化）
        nearest_food = self._get_nearest_resource("food")
        nearest_water = self._get_nearest_resource("water")
        nearest_ore = self._get_nearest_resource("ore")
        state.extend([
            nearest_food / 100.0,  # 归一化距离
            nearest_water / 100.0,
            nearest_ore / 100.0,
        ])

        # 5. 感知信息：可见实体数量、最近的人类距离、最近的动物距离
        vision = self.world.get_component(self.entity_id, VisionComponent)
        if vision:
            # 可见实体数量（归一化）
            num_visible = min(len(vision.entity_ids) / 20.0, 1.0)
            state.append(num_visible)

            # 最近的人类距离
            nearest_human = self._get_nearest_entity(HumanComponent)
            state.append(nearest_human / 100.0)

            # 最近的动物距离（可能的危险）
            nearest_animal = self._get_nearest_entity(AnimalComponent)
            state.append(nearest_animal / 100.0)
        else:
            state.extend([0.0] * 3)

        # 6. 天气信息：温度、湿度、降水（从环境系统获取）
        weather_info = self._get_weather_info()
        state.extend(weather_info)

        # 7. 定居点信息：最近的定居点距离、定居点类型
        settlement_info = self._get_settlement_info()
        state.extend(settlement_info)

        # 8. 危险信息：是否有捕食者附近、是否有自然灾害
        danger_info = self._get_danger_info()
        state.extend(danger_info)

        # 9. 社交信息：附近的人类数量、是否有朋友附近
        social_info = self._get_social_info()
        state.extend(social_info)

        # 10. 记忆：最近成功的动作（one-hot编码）
        memory = self.world.get_component(self.entity_id, MemoryComponent)
        if memory:
            # 简化：使用最近成功的动作作为状态
            recent_success = [0.0] * len(self.actions)
            for action, count in memory.recent_successes.items():
                if action in [a.name.lower() for a in self.actions]:
                    idx = [a.name.lower() for a in self.actions].index(action)
                    recent_success[idx] = min(count / 10.0, 1.0)
            state.extend(recent_success)
        else:
            state.extend([0.0] * len(self.actions))

        # 确保状态向量长度正确
        while len(state) < self.state_space_size:
            state.append(0.0)
        state = state[:self.state_space_size]

        return np.array(state, dtype=np.float32)

    def _get_nearest_resource(self, resource_type: str) -> float:
        """获取最近的资源距离"""
        pos = self.world.get_component(self.entity_id, SpaceComponent)
        if not pos:
            return 100.0  # 默认最大距离

        # 查找所有资源
        min_distance = 100.0
        for e, (resource, res_pos) in self.world.get_components(ResourceComponent, SpaceComponent):
            if resource_type == "food" and resource.resource_type == "food":
                distance = ((pos.x - res_pos.x)**2 + (pos.y - res_pos.y)**2)**0.5
                if distance < min_distance:
                    min_distance = distance
            elif resource_type == "water" and resource.resource_type == "water":
                distance = ((pos.x - res_pos.x)**2 + (pos.y - res_pos.y)**2)**0.5
                if distance < min_distance:
                    min_distance = distance
            elif resource_type == "ore" and resource.resource_type == "ore":
                distance = ((pos.x - res_pos.x)**2 + (pos.y - res_pos.y)**2)**0.5
                if distance < min_distance:
                    min_distance = distance

        return min_distance

    def _get_nearest_entity(self, component_type) -> float:
        """获取最近的实体距离"""
        pos = self.world.get_component(self.entity_id, SpaceComponent)
        if not pos:
            return 100.0

        min_distance = 100.0
        for e, (comp, entity_pos) in self.world.get_components(component_type, SpaceComponent):
            if e.id == self.entity_id:
                continue
            distance = ((pos.x - entity_pos.x)**2 + (pos.y - entity_pos.y)**2)**0.5
            if distance < min_distance:
                min_distance = distance

        return min_distance

    def _get_weather_info(self) -> List[float]:
        """获取天气信息"""
        # 这里简化处理，实际应该从天气系统获取
        # 温度（-20~40归一化到0-1）
        temperature = 0.5  # 默认25度
        # 湿度（0~100归一化到0-1）
        humidity = 0.5
        # 降水（0~1）
        precipitation = 0.0
        # 光照（0~1）
        light = 1.0
        return [temperature, humidity, precipitation, light]

    def _get_settlement_info(self) -> List[float]:
        """获取定居点信息"""
        pos = self.world.get_component(self.entity_id, SpaceComponent)
        if not pos:
            return [100.0, 0.0, 0.0]  # 距离、类型、人口

        min_distance = 100.0
        settlement_type = 0.0  # 0=无, 1=营地, 2=村庄, 3=城镇, 4=城市
        settlement_population = 0.0

        for e, (settlement, settlement_pos) in self.world.get_components(SettlementComponent, SpaceComponent):
            distance = ((pos.x - settlement_pos.x)**2 + (pos.y - settlement_pos.y)**2)**0.5
            if distance < min_distance:
                min_distance = distance
                # 定居点类型映射到0-1
                settlement_type = settlement.settlement_type.value / 4.0
                settlement_population = min(settlement.population / 1000.0, 1.0)

        return [min_distance / 100.0, settlement_type, settlement_population]

    def _get_danger_info(self) -> List[float]:
        """获取危险信息"""
        # 是否有捕食者附近
        predator_nearby = 0.0
        # 是否有自然灾害
        natural_disaster = 0.0
        # 健康状态（反向）
        needs = self.world.get_component(self.entity_id, PhysiologyNeedsComponent)
        health_danger = 1.0 - (needs.health / 100.0 if needs else 1.0)

        return [predator_nearby, natural_disaster, health_danger]

    def _get_social_info(self) -> List[float]:
        """获取社交信息"""
        pos = self.world.get_component(self.entity_id, SpaceComponent)
        if not pos:
            return [0.0, 0.0, 0.0]  # 附近人类数量、朋友数量、社交需求

        # 附近的人类数量（10单位内）
        nearby_humans = 0
        for e, (human, human_pos) in self.world.get_components(HumanComponent, SpaceComponent):
            if e.id == self.entity_id:
                continue
            distance = ((pos.x - human_pos.x)**2 + (pos.y - human_pos.y)**2)**0.5
            if distance < 10.0:
                nearby_humans += 1

        # 朋友数量（从记忆组件获取）
        memory = self.world.get_component(self.entity_id, MemoryComponent)
        friend_count = 0
        if memory:
            friend_count = len(memory.people)

        # 社交需求（反向）
        needs = self.world.get_component(self.entity_id, PhysiologyNeedsComponent)
        social_need = 1.0 - (needs.social / 100.0 if needs else 1.0)

        return [
            min(nearby_humans / 10.0, 1.0),
            min(friend_count / 20.0, 1.0),
            social_need
        ]

    def step(self, action_idx: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """
        执行动作，返回新状态、奖励、是否结束、信息
        Args:
            action_idx: 动作索引
        Returns:
            (next_state, reward, done, info)
        """
        # 这里不实际执行动作，而是由ECS系统执行
        # 我们只需要计算奖励
        action = self.actions[action_idx]
        reward = self._calculate_reward(action)
        next_state = self.get_state()
        done = self._check_done()
        info = {"action": action.name}
        return next_state, reward, done, info

    def _calculate_reward(self, action: IntentType) -> float:
        """计算奖励函数，考虑更多因素"""
        needs = self.world.get_component(self.entity_id, PhysiologyNeedsComponent)
        if not needs:
            return 0.0

        reward = 0.0

        # 1. 生存奖励：存活每一帧获得小奖励
        reward += 0.1

        # 2. 需求满足奖励
        if action == IntentType.EAT and needs.hunger < 30:
            reward += 1.0  # 吃了之后不饿了，奖励
        elif action == IntentType.DRINK and needs.thirst < 30:
            reward += 1.0
        elif action == IntentType.SLEEP and needs.energy > 80:
            reward += 1.0
        elif action == IntentType.SOCIALIZE and needs.social > 80:
            reward += 0.5
        elif action == IntentType.WORK:
            # 工作获得资源，长期奖励
            reward += 0.3
        elif action == IntentType.BUILD:
            # 建造定居点，长期奖励
            reward += 0.5
        elif action == IntentType.TRADE:
            # 交易获得资源，长期奖励
            reward += 0.4

        # 3. 惩罚：如果需求很低但没采取对应行动
        if needs.hunger > 70 and action != IntentType.EAT:
            reward -= 0.5
        if needs.thirst > 70 and action != IntentType.DRINK:
            reward -= 0.5
        if needs.energy < 20 and action != IntentType.SLEEP:
            reward -= 0.5
        if needs.social < 20 and action != IntentType.SOCIALIZE:
            reward -= 0.3

        # 4. 危险惩罚：如果有危险但没逃跑
        danger_info = self._get_danger_info()
        if danger_info[0] > 0.5 and action != IntentType.FLEE:
            reward -= 1.0
        if danger_info[2] > 0.7 and action != IntentType.SLEEP:
            reward -= 0.5

        return reward

    def _check_done(self) -> bool:
        """检查是否结束（死亡）"""
        needs = self.world.get_component(self.entity_id, PhysiologyNeedsComponent)
        if not needs:
            return True
        # 死亡条件：健康值为0
        return needs.health <= 0

    def reset(self):
        """重置环境"""
        # 不需要重置，ECS世界由外部管理
        return self.get_state()