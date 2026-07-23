#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动作规划系统：根据目标自动规划动作元件序列
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
from core.world import World
from human.rl.action_primitives import ActionPrimitive, ActionSequence, ActionPrimitiveType, get_action_primitive

@dataclass
class Goal:
    """行为目标"""
    type: str                              # 目标类型：survive/socialize/explore/build等
    target_entity: Optional[int] = None     # 目标实体
    target_position: Optional[Tuple[float, float]] = None  # 目标位置
    target_item: Optional[int] = None       # 目标物品
    priority: float = 1.0                   # 目标优先级
    is_complete: bool = False               # 目标是否完成
    is_failed: bool = False                 # 目标是否失败

class ActionPlanner:
    """动作规划器：根据目标生成动作序列"""

    def __init__(self, world: World, entity_id: int):
        self.world = world
        self.entity_id = entity_id

    def plan(self, goal: Goal) -> Optional[ActionSequence]:
        """根据目标规划动作序列"""
        if goal.type == "survive":
            return self._plan_survive(goal)
        elif goal.type == "socialize":
            return self._plan_socialize(goal)
        elif goal.type == "explore":
            return self._plan_explore(goal)
        elif goal.type == "build":
            return self._plan_build(goal)
        elif goal.type == "work":
            return self._plan_work(goal)
        elif goal.type == "flee":
            return self._plan_flee(goal)
        else:
            # 默认返回空序列
            return ActionSequence()

    def _plan_survive(self, goal: Goal) -> ActionSequence:
        """规划生存目标：吃/喝/休息"""
        from biology.components.physiology_needs_component import PhysiologyNeedsComponent
        from human.components.economic.inventory.inventory_component import InventoryComponent
        from resource.components.resource_component import ResourceComponent
        from space.space_component import SpaceComponent

        needs = self.world.get_component(self.entity_id, PhysiologyNeedsComponent)
        inventory = self.world.get_component(self.entity_id, InventoryComponent)
        pos = self.world.get_component(self.entity_id, SpaceComponent)

        if not needs or not pos:
            return ActionSequence()

        sequence = ActionSequence()

        # 1. 检查是否有食物/水在库存中
        if needs.hunger > 50:
            # 查找库存中的食物
            food_item = None
            if inventory:
                for item_key, amount in inventory.items.items():
                    if "food" in str(item_key) and amount > 0:
                        food_item = item_key
                        break

            if food_item:
                # 直接消耗食物
                sequence.primitives.append(get_action_primitive(ActionPrimitiveType.CONSUME, item_id=food_item))
            else:
                # 查找附近的食物资源
                nearest_food = self._find_nearest_resource("food")
                if nearest_food:
                    # 移动到食物位置
                    food_pos = self.world.get_component(nearest_food, SpaceComponent)
                    sequence.primitives.append(get_action_primitive(ActionPrimitiveType.MOVE_TO, x=food_pos.x, y=food_pos.y))
                    # 抓取食物
                    sequence.primitives.append(get_action_primitive(ActionPrimitiveType.GRAB, target_entity=nearest_food))
                    # 消耗食物
                    sequence.primitives.append(get_action_primitive(ActionPrimitiveType.CONSUME, item_id=hash(nearest_food)))
                else:
                    # 没有找到食物，休息恢复能量
                    sequence.primitives.append(get_action_primitive(ActionPrimitiveType.REST, duration=5.0))

        # 2. 检查是否需要喝水
        if needs.thirst > 50:
            # 查找库存中的水
            water_item = None
            if inventory:
                for item_key, amount in inventory.items.items():
                    if "water" in str(item_key) and amount > 0:
                        water_item = item_key
                        break

            if water_item:
                # 直接消耗水
                sequence.primitives.append(get_action_primitive(ActionPrimitiveType.CONSUME, item_id=water_item))
            else:
                # 查找附近的水资源
                nearest_water = self._find_nearest_resource("water")
                if nearest_water:
                    # 移动到水位置
                    water_pos = self.world.get_component(nearest_water, SpaceComponent)
                    sequence.primitives.append(get_action_primitive(ActionPrimitiveType.MOVE_TO, x=water_pos.x, y=water_pos.y))
                    # 抓取水
                    sequence.primitives.append(get_action_primitive(ActionPrimitiveType.GRAB, target_entity=nearest_water))
                    # 消耗水
                    sequence.primitives.append(get_action_primitive(ActionPrimitiveType.CONSUME, item_id=hash(nearest_water)))
                else:
                    # 没有找到水，休息恢复能量
                    sequence.primitives.append(get_action_primitive(ActionPrimitiveType.REST, duration=5.0))

        # 3. 检查是否需要休息
        if needs.energy < 30:
            sequence.primitives.append(get_action_primitive(ActionPrimitiveType.REST, duration=10.0))

        # 如果没有任何动作，默认休息
        if len(sequence.primitives) == 0:
            sequence.primitives.append(get_action_primitive(ActionPrimitiveType.REST, duration=5.0))

        return sequence

    def _plan_socialize(self, goal: Goal) -> ActionSequence:
        """规划社交目标"""
        from human.components.basic.human_component import HumanComponent
        from space.space_component import SpaceComponent

        pos = self.world.get_component(self.entity_id, SpaceComponent)
        if not pos:
            return ActionSequence()

        sequence = ActionSequence()

        # 查找附近的人类
        nearest_human = self._find_nearest_entity(HumanComponent)
        if nearest_human:
            # 移动到人类位置
            human_pos = self.world.get_component(nearest_human, SpaceComponent)
            sequence.primitives.append(get_action_primitive(ActionPrimitiveType.MOVE_TO, x=human_pos.x, y=human_pos.y))
            # 社交
            sequence.primitives.append(get_action_primitive(ActionPrimitiveType.SOCIALIZE, target_entity=nearest_human))

        return sequence

    def _plan_explore(self, goal: Goal) -> ActionSequence:
        """规划探索目标"""
        import random
        from space.space_component import SpaceComponent

        pos = self.world.get_component(self.entity_id, SpaceComponent)
        if not pos:
            return ActionSequence()

        sequence = ActionSequence()

        # 随机选择一个方向探索
        angle = random.uniform(0, 2 * np.pi)
        distance = random.uniform(10, 20)
        target_x = pos.x + distance * np.cos(angle)
        target_y = pos.y + distance * np.sin(angle)

        # 移动到目标位置
        sequence.primitives.append(get_action_primitive(ActionPrimitiveType.MOVE_TO, x=target_x, y=target_y))
        # 调查周围环境
        sequence.primitives.append(get_action_primitive(ActionPrimitiveType.INVESTIGATE))

        return sequence

    def _plan_build(self, goal: Goal) -> ActionSequence:
        """规划建造目标"""
        # 简化处理，实际需要检查资源、工具等
        sequence = ActionSequence()
        sequence.primitives.append(get_action_primitive(ActionPrimitiveType.BUILD))
        return sequence

    def _plan_work(self, goal: Goal) -> ActionSequence:
        """规划工作目标：采集/制作"""
        from resource.components.resource_component import ResourceComponent
        from space.space_component import SpaceComponent

        pos = self.world.get_component(self.entity_id, SpaceComponent)
        if not pos:
            return ActionSequence()

        sequence = ActionSequence()

        # 查找附近的资源
        nearest_resource = self._find_nearest_resource("any")
        if nearest_resource:
            # 移动到资源位置
            resource_pos = self.world.get_component(nearest_resource, SpaceComponent)
            sequence.primitives.append(get_action_primitive(ActionPrimitiveType.MOVE_TO, x=resource_pos.x, y=resource_pos.y))
            # 采集资源
            sequence.primitives.append(get_action_primitive(ActionPrimitiveType.GATHER, target_entity=nearest_resource))

        return sequence

    def _plan_flee(self, goal: Goal) -> ActionSequence:
        """规划逃跑目标"""
        sequence = ActionSequence()
        sequence.primitives.append(get_action_primitive(ActionPrimitiveType.FLEE))
        return sequence

    def _find_nearest_resource(self, resource_type: str) -> Optional[int]:
        """查找最近的资源实体"""
        from resource.components.resource_component import ResourceComponent
        from space.space_component import SpaceComponent

        pos = self.world.get_component(self.entity_id, SpaceComponent)
        if not pos:
            return None

        nearest_entity = None
        min_distance = float('inf')

        for e, (resource, res_pos) in self.world.get_components(ResourceComponent, SpaceComponent):
            if resource_type != "any" and resource.resource_type != resource_type:
                continue
            distance = ((pos.x - res_pos.x)**2 + (pos.y - res_pos.y)**2)**0.5
            if distance < min_distance:
                min_distance = distance
                nearest_entity = e.id

        return nearest_entity

    def _find_nearest_entity(self, component_type) -> Optional[int]:
        """查找最近的实体"""
        from space.space_component import SpaceComponent

        pos = self.world.get_component(self.entity_id, SpaceComponent)
        if not pos:
            return None

        nearest_entity = None
        min_distance = float('inf')

        for e, (comp, entity_pos) in self.world.get_components(component_type, SpaceComponent):
            if e.id == self.entity_id:
                continue
            distance = ((pos.x - entity_pos.x)**2 + (pos.y - entity_pos.y)**2)**0.5
            if distance < min_distance:
                min_distance = distance
                nearest_entity = e.id

        return nearest_entity