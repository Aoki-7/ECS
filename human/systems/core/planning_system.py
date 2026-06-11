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
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from core.components.vision_component import VisionComponent


class PlanningSystem(System):
    tick_interval = 1  # 每帧执行一次，避免意图到行动的响应滞后导致饿死/渴死
    """
    把意图转换为行为序列
    """

    EXPLORE_RADIUS = 20  # 探索半径

    def __init__(self):
        super().__init__()

    def update(self, world: World, dt: float):
        from core.components.world_config_component import WorldConfigComponent
        world_config = world.get_world_component(WorldConfigComponent)
        planned_this_tick = set()

        for entity, (intent, task, action, space) in world.get_components(
            IntentComponent, TaskComponent, ActionComponent, SpaceComponent
        ):
            if entity.id in planned_this_tick:
                continue
            if action.action_queue:
                continue
            
            self._process_planning(entity, intent, task, action, space, world, world_config, planned_this_tick)

    def _process_planning(self, entity, intent, task, action, space, world, world_config, planned_this_tick):
        """处理单个实体的规划逻辑"""
        needs = world.get_component(entity, PhysiologyNeedsComponent)
        is_critical = needs and (needs.hunger > 90 or needs.thirst > 90)
        
        # 检查是否允许规划
        if not self._should_plan(action, is_critical, needs):
            return
        
        # 执行意图规划
        self._plan_by_intent(entity, intent, task, action, space, world, world_config)
        planned_this_tick.add(entity.id)

    def _should_plan(self, action, is_critical, needs) -> bool:
        """判断当前状态是否允许规划"""
        # 非危险状态下，执行具体动作时不规划
        if not is_critical and action.current_action not in (
            ActionType.IDLE, ActionType.MOVE_TO, ActionType.SLEEP, ActionType.EAT, ActionType.DRINK
        ):
            return False
        
        # 危险状态下中断移动/进食/饮水
        if is_critical and action.current_action in (ActionType.MOVE_TO, ActionType.EAT, ActionType.DRINK):
            self._interrupt_action(action)
            return True
        
        # 中断移动以便新规划
        if action.current_action == ActionType.MOVE_TO:
            self._interrupt_action(action)
            return True
        
        # 睡眠中检查是否需中断
        if action.current_action == ActionType.SLEEP:
            if needs and (needs.hunger > 85 or needs.thirst > 85):
                self._interrupt_action(action)
                return True
            return False
        
        return True

    def _interrupt_action(self, action) -> None:
        """中断当前动作"""
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.IDLE
        action.progress = 0.0

    def _plan_by_intent(self, entity, intent, task, action, space, world, world_config):
        """根据意图规划行为队列"""
        if intent.intent == IntentType.EAT:
            self._plan_eat(entity, task, action, world)
        elif intent.intent == IntentType.DRINK:
            self._plan_drink(entity, task, action, world)
        elif intent.intent == IntentType.SLEEP:
            self._plan_sleep(task, action)
        elif intent.intent == IntentType.EXPLORE:
            self._plan_explore(entity, task, action, space, world, world_config)
        elif intent.intent == IntentType.PAIR:
            self._plan_pair(task, action)

    def _plan_eat(self, entity, task, action, world) -> None:
        """规划进食行为"""
        task.task = TaskType.FIND_FOOD
        task.status = TaskStatus.RUNNING

        inventory = world.get_component(entity, InventoryComponent)
        has_food = inventory is not None and inventory.find(FoodComponent, world) is not None
        if has_food:
            action.action_queue = [ActionType.EAT]
            return

        nearby_plant = self._find_harvestable_plant(entity, world)
        if nearby_plant is not None:
            action.target_entity = nearby_plant.id
            action.action_queue = [ActionType.MOVE_TO, ActionType.HARVEST, ActionType.EAT]
        else:
            action.action_queue = [ActionType.SEARCH, ActionType.MOVE_TO, ActionType.PICKUP, ActionType.EAT]

    def _plan_drink(self, entity, task, action, world) -> None:
        """规划饮水行为"""
        task.task = TaskType.DRINK_WATER
        task.status = TaskStatus.RUNNING

        inventory = world.get_component(entity, InventoryComponent)
        has_water = inventory is not None and inventory.find(WaterComponent, world) is not None
        if has_water:
            action.action_queue = [ActionType.DRINK]
        else:
            action.action_queue = [ActionType.SEARCH, ActionType.MOVE_TO, ActionType.DRINK]
            # SEARCH 会设置 target_pos，然后 MOVE_TO 使用它

    def _plan_sleep(self, task, action) -> None:
        """规划睡眠行为"""
        task.task = TaskType.SLEEP
        task.status = TaskStatus.RUNNING
        action.action_queue = [ActionType.SLEEP]

    def _plan_explore(self, entity, task, action, space, world, world_config) -> None:
        """规划探索行为"""
        task.task = TaskType.EXPLORE
        task.status = TaskStatus.RUNNING

        memory = world.get_component(entity, MemoryComponent)
        explore_target = self._find_explore_target(memory)
        
        if explore_target:
            action.target_pos = explore_target
        else:
            target_x = space.x + random.randint(-self.EXPLORE_RADIUS, self.EXPLORE_RADIUS)
            target_y = space.y + random.randint(-self.EXPLORE_RADIUS, self.EXPLORE_RADIUS)
            target_x, target_y = world_config.clamp_position(target_x, target_y)
            action.target_pos = (target_x, target_y)

        action.action_queue = [ActionType.MOVE_TO]

    def _find_explore_target(self, memory):
        """从记忆中查找探索目标"""
        if not memory or not memory.places:
            return None
        
        positive_places = [
            (pos, info) for pos, info in memory.places.items()
            if info.get("sentiment", 0) > 0.2
        ]
        if not positive_places:
            return None
        
        positive_places.sort(key=lambda x: x[1]["sentiment"], reverse=True)
        best = random.choice(positive_places[:3])
        return best[0]

    def _plan_pair(self, task, action) -> None:
        """规划配对行为"""
        task.task = TaskType.FIND_PARTNER
        task.status = TaskStatus.RUNNING
        action.action_queue = [ActionType.SEARCH, ActionType.MOVE_TO, ActionType.SOCIALIZE]

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