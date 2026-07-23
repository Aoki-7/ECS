#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:planning_system.py
@说明:步骤规划系统
@时间:2026/04/01 15:35:35
@作者:Sherry
@版本:3.0

v3.0 拆分：
- 规划决策 -> PlanningDecisionMaker
- 行为规划 -> ActionPlanner
- 资源查找 -> ResourceFinder
'''

import random

from core.system import System
from core.world import World

from human.components.cognitive.intent_component import IntentComponent, IntentType
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from space.space_component import SpaceComponent

from human.systems.core.planning_decision_maker import PlanningDecisionMaker
from human.systems.core.action_planner import ActionPlanner
from human.systems.core.resource_finder import ResourceFinder


class PlanningSystem(System):
    tick_interval = 1  # 每帧执行一次，避免意图到行动的响应滞后导致饿死/渴死
    """
    把意图转换为行为序列
    """

    EXPLORE_RADIUS = 20  # 探索半径

    def __init__(self):
        super().__init__()
        self._decision_maker = PlanningDecisionMaker()
        self._action_planner = ActionPlanner()
        self._resource_finder = ResourceFinder()

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
        from biology.components.physiology_needs_component import PhysiologyNeedsComponent
        needs = world.get_component(entity, PhysiologyNeedsComponent)
        is_critical = needs and (needs.hunger > 90 or needs.thirst > 90)

        # 检查是否允许规划
        if not self._decision_maker.should_plan(action, is_critical, needs):
            return

        # 执行意图规划
        self._action_planner.plan_by_intent(entity, intent, task, action, space, world, world_config, self._resource_finder)
        planned_this_tick.add(entity.id)

    # 向后兼容的委托方法
    def _should_plan(self, action, is_critical, needs) -> bool:
        return self._decision_maker.should_plan(action, is_critical, needs)

    def _interrupt_action(self, action) -> None:
        self._decision_maker.interrupt_action(action)

    def _plan_by_intent(self, entity, intent, task, action, space, world, world_config):
        self._action_planner.plan_by_intent(entity, intent, task, action, space, world, world_config, self._resource_finder)

    def _plan_eat(self, entity, task, action, world) -> None:
        self._action_planner.plan_eat(entity, task, action, world, self._resource_finder)

    def _plan_drink(self, entity, task, action, world) -> None:
        self._action_planner.plan_drink(entity, task, action, world, self._resource_finder)

    def _plan_sleep(self, task, action) -> None:
        self._action_planner.plan_sleep(task, action)

    def _plan_explore(self, entity, task, action, space, world, world_config) -> None:
        self._action_planner.plan_explore(entity, task, action, space, world, world_config)

    def _plan_pair(self, task, action) -> None:
        self._action_planner.plan_pair(task, action)

    def _find_harvestable_plant(self, entity, world):
        return self._resource_finder.find_harvestable_plant(entity, world)

    def _find_resource_in_memory(self, entity, world, resource_type):
        return self._resource_finder.find_resource_in_memory(entity, world, resource_type)

    def _find_nearest_resource(self, entity, world, resource_type):
        return self._resource_finder.find_nearest_resource(entity, world, resource_type)