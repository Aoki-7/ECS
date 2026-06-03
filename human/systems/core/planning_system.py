#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:planning_system.py
@说明:步骤规划系统
@时间:2026/04/01 15:35:35
@作者:Sherry
@版本:2.0
'''

"""Intent -> ActionQueue"""

import random

from core.system import System
from core.world import World

from human.components.cognitive.intent_component import IntentComponent, IntentType
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from core.components.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from resource.food.components.food_component import FoodComponent
from resource.water.components.water_component import WaterComponent
from resource.components.resource_component import ResourceComponent
from biology.components.life_cycle_component import LifeCycleComponent
from core.components.vision_component import VisionComponent


class PlanningSystem(System):
    tick_interval = 1  # 每帧执行一次，避免意图到行动的响应滞后导致饿死/渴死
    """
    把意图转换为行为序列
    """

    EXPLORE_RADIUS = 20  # 探索半径

    def __init__(self):
        super().__init__()

    def update(self, world: World, dt):
        planned_this_tick = set()

        for entity, (intent, task, action, space) in world.get_components(
            IntentComponent, TaskComponent, ActionComponent, SpaceComponent
        ):
            
            intent: IntentComponent
            task: TaskComponent
            action: ActionComponent
            space: SpaceComponent

            # 防止同 tick 重复规划
            if entity.id in planned_this_tick:
                continue

            # 已有明确的后续任务队列时不重复规划
            if action.action_queue:
                continue
            # 检查当前是否处于危险生理状态，如果是则允许中断任何动作
            needs = world.get_component(entity, PhysiologyNeedsComponent)
            is_critical = needs and (needs.hunger > 90 or needs.thirst > 90)
            
            # 当前正在执行某些具体动作（非移动/非空闲/非睡眠/非进食/非饮水）时不规划
            if not is_critical and action.current_action not in (ActionType.IDLE, ActionType.MOVE_TO, ActionType.SLEEP, ActionType.EAT, ActionType.DRINK):
                continue
            
            # 如果正在移动/进食/饮水但生理需求达到危险水平，中断当前动作
            if is_critical and action.current_action in (ActionType.MOVE_TO, ActionType.EAT, ActionType.DRINK):
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.IDLE
                action.progress = 0.0
            
            # 如果正在移动中（非危险），中断当前移动以便执行新规划
            if action.current_action == ActionType.MOVE_TO:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.IDLE
                action.progress = 0.0
            
            # 如果正在睡眠但生理需求达到危险水平，中断睡眠
            if action.current_action == ActionType.SLEEP:
                if needs and (needs.hunger > 85 or needs.thirst > 85):
                    action.current_action = ActionType.IDLE
                    action.status = ActionStatus.IDLE
                    action.progress = 0.0
                else:
                    continue

            if intent.intent == IntentType.EAT:
                task.task = TaskType.FIND_FOOD
                task.status = TaskStatus.RUNNING

                # 如果背包有食物，直接吃，无需搜索
                inventory = world.get_component(entity, InventoryComponent)
                has_food = inventory is not None and inventory.find(FoodComponent, world) is not None
                if has_food:
                    action.action_queue = [ActionType.EAT]
                else:
                    # 检查视野内是否有可收获植物（成熟状态）
                    nearby_plant = self._find_harvestable_plant(entity, world)
                    if nearby_plant is not None:
                        # 规划收获：搜索→移动→收获→进食
                        action.action_queue = [
                            ActionType.SEARCH,
                            ActionType.MOVE_TO,
                            ActionType.HARVEST,
                            ActionType.EAT
                        ]
                    else:
                        action.action_queue = [
                            ActionType.SEARCH,
                            ActionType.MOVE_TO,
                            ActionType.PICKUP,
                            ActionType.EAT
                        ]

            elif intent.intent == IntentType.DRINK:
                task.task = TaskType.DRINK_WATER
                task.status = TaskStatus.RUNNING

                # 如果背包有水，直接喝，无需搜索
                inventory = world.get_component(entity, InventoryComponent)
                has_water = inventory is not None and inventory.find(WaterComponent, world) is not None
                if has_water:
                    action.action_queue = [ActionType.DRINK]
                else:
                    action.action_queue = [
                        ActionType.SEARCH,
                        ActionType.MOVE_TO,
                        ActionType.DRINK
                    ]

            elif intent.intent == IntentType.SLEEP:
                task.task = TaskType.SLEEP
                task.status = TaskStatus.RUNNING

                # 原地睡眠，无需移动
                action.action_queue = [
                    ActionType.SLEEP
                ]

            elif intent.intent == IntentType.EXPLORE:
                task.task = TaskType.EXPLORE
                task.status = TaskStatus.RUNNING

                # 优先参考记忆中的高情感地点作为探索目标
                memory = world.get_component(entity, MemoryComponent)
                explore_target = None
                if memory and memory.places:
                    # 筛选有正面情感的地点，按情感排序
                    positive_places = [
                        (pos, info) for pos, info in memory.places.items()
                        if info.get("sentiment", 0) > 0.2
                    ]
                    if positive_places:
                        positive_places.sort(key=lambda x: x[1]["sentiment"], reverse=True)
                        # 从前3个好地点中随机选一个（避免总是去同一个地方）
                        best = random.choice(positive_places[:3])
                        explore_target = best[0]
                
                if explore_target:
                    action.target_pos = explore_target
                else:
                    # 无记忆时随机选择一个探索目标
                    target_x = space.x + random.randint(-self.EXPLORE_RADIUS, self.EXPLORE_RADIUS)
                    target_y = space.y + random.randint(-self.EXPLORE_RADIUS, self.EXPLORE_RADIUS)
                    # 限制在地图范围内
                    target_x = max(0, min(99, target_x))
                    target_y = max(0, min(99, target_y))
                    action.target_pos = (target_x, target_y)

                action.action_queue = [
                    ActionType.MOVE_TO,
                ]

            elif intent.intent == IntentType.PAIR:
                task.task = TaskType.FIND_PARTNER
                task.status = TaskStatus.RUNNING

                action.action_queue = [
                    ActionType.SEARCH,
                    ActionType.MOVE_TO,
                    ActionType.SOCIALIZE
                ]

            planned_this_tick.add(entity.id)

    def _find_harvestable_plant(self, entity, world: World):
        """在视野内查找可收获的植物实体"""
        from plant.components.plant_component import PlantComponent
        
        space = world.get_component(entity, SpaceComponent)
        vision = world.get_component(entity, VisionComponent)
        if space is None or vision is None:
            return None
        
        radius = getattr(vision, 'radius', 15)
        
        # 通过空间索引查询附近的实体
        space_system = getattr(world, 'space_system', None)
        if space_system is not None:
            for candidate_id in space_system.neighbors(space.x, space.y, radius, space.layer):
                candidate = world.get_entity(candidate_id)
                if candidate is None:
                    continue
                plant_comp = world.get_component(candidate, PlantComponent)
                lifecycle = world.get_component(candidate, LifeCycleComponent)
                if plant_comp is None or lifecycle is None:
                    continue
                # 检查是否成熟
                if lifecycle.stage >= plant_comp.harvest_stage:
                    return candidate
        
        # 兜底：遍历所有植物
        for candidate, (plant_comp, lifecycle, c_space) in world.get_components(PlantComponent, LifeCycleComponent, SpaceComponent):
            dx = abs(c_space.x - space.x)
            dy = abs(c_space.y - space.y)
            if dx <= radius and dy <= radius:
                if lifecycle.stage >= plant_comp.harvest_stage:
                    return candidate
        
        return None