#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:action_planner.py
@说明:行为规划器

职责：
    - 根据意图规划行为队列
    - 进食/饮水/睡眠/探索/配对等行为规划
'''

import random

from human.components.cognitive.intent_component import IntentComponent, IntentType
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.action.action_component import ActionComponent, ActionType


class ActionPlanner:
    """行为规划器"""

    def plan_by_intent(self, entity, intent: IntentComponent, task: TaskComponent,
                       action: ActionComponent, space, world, world_config, resource_finder):
        """根据意图规划行为队列"""
        if intent.intent == IntentType.EAT:
            self.plan_eat(entity, task, action, world, resource_finder)
        elif intent.intent == IntentType.DRINK:
            self.plan_drink(entity, task, action, world, resource_finder)
        elif intent.intent == IntentType.SLEEP:
            self.plan_sleep(task, action)
        elif intent.intent == IntentType.EXPLORE:
            self.plan_explore(entity, task, action, space, world, world_config)
        elif intent.intent == IntentType.PAIR:
            self.plan_pair(task, action)

    def plan_eat(self, entity, task: TaskComponent, action: ActionComponent, world, resource_finder) -> None:
        """规划进食行为"""
        task.task = TaskType.FIND_FOOD
        task.status = TaskStatus.RUNNING

        from human.components.economic.inventory.inventory_component import InventoryComponent
        from resource.food.components.food_component import FoodComponent

        inventory = world.get_component(entity, InventoryComponent)
        # 防御：InventoryComponent 可能没有 find 方法
        if inventory is not None and hasattr(inventory, 'find'):
            has_food = inventory.find(FoodComponent, world) is not None
        else:
            # 简单检查：items 字典中是否有 FoodComponent 类型的实体
            has_food = False
            if inventory and hasattr(inventory, 'items'):
                for item_id in inventory.items:
                    if world.get_component(item_id, FoodComponent) is not None:
                        has_food = True
                        break
        if has_food:
            action.action_queue = [ActionType.EAT]
            return

        nearby_plant = resource_finder.find_harvestable_plant(entity, world)
        if nearby_plant is not None:
            action.target_entity = nearby_plant.id
            action.action_queue = [ActionType.MOVE_TO, ActionType.HARVEST, ActionType.EAT]
        else:
            action.action_queue = [ActionType.SEARCH, ActionType.MOVE_TO, ActionType.PICKUP, ActionType.EAT]

    def plan_drink(self, entity, task: TaskComponent, action: ActionComponent, world, resource_finder) -> None:
        """规划饮水行为"""
        task.task = TaskType.DRINK_WATER
        task.status = TaskStatus.RUNNING

        from human.components.economic.inventory.inventory_component import InventoryComponent
        from resource.water.components.water_component import WaterComponent

        inventory = world.get_component(entity, InventoryComponent)
        # 防御：InventoryComponent 可能没有 find 方法
        if inventory is not None and hasattr(inventory, 'find'):
            has_water = inventory.find(WaterComponent, world) is not None
        else:
            # 简单检查：items 字典中是否有 WaterComponent 类型的实体
            has_water = False
            if inventory and hasattr(inventory, 'items'):
                for item_id in inventory.items:
                    if world.get_component(item_id, WaterComponent) is not None:
                        has_water = True
                        break
        if has_water:
            action.action_queue = [ActionType.DRINK]
            return

        # 查找记忆中的水源
        water_source = resource_finder.find_resource_in_memory(entity, world, "water")
        if water_source is not None:
            action.target_entity = water_source
            action.action_queue = [ActionType.MOVE_TO, ActionType.DRINK]
        else:
            action.action_queue = [ActionType.SEARCH, ActionType.MOVE_TO, ActionType.DRINK]

    def plan_sleep(self, task: TaskComponent, action: ActionComponent) -> None:
        """规划睡眠行为"""
        task.task = TaskType.SLEEP
        task.status = TaskStatus.RUNNING
        action.action_queue = [ActionType.SLEEP]

    def plan_explore(self, entity, task: TaskComponent, action: ActionComponent,
                     space, world, world_config) -> None:
        """规划探索行为"""
        task.task = TaskType.EXPLORE
        task.status = TaskStatus.RUNNING

        # 防御：检查 space 是否为 None
        if space is None:
            # 使用默认位置
            space_x, space_y = 0, 0
        else:
            space_x = getattr(space, 'x', 0)
            space_y = getattr(space, 'y', 0)

        # 随机选择探索方向
        radius = getattr(world_config, 'explore_radius', 20) if world_config else 20
        angle = random.uniform(0, 2 * 3.14159)
        target_x = int(space_x + radius * random.uniform(0.5, 1.0) * (1 if angle < 3.14159 else -1))
        target_y = int(space_y + radius * random.uniform(0.5, 1.0) * (1 if angle < 3.14159 else -1))

        action.target_x = target_x
        action.target_y = target_y
        action.action_queue = [ActionType.EXPLORE, ActionType.MOVE_TO]

    def plan_pair(self, task: TaskComponent, action: ActionComponent) -> None:
        """规划配对行为"""
        task.task = TaskType.FIND_MATE
        task.status = TaskStatus.RUNNING
        action.action_queue = [ActionType.SEARCH, ActionType.MOVE_TO, ActionType.PAIR]
