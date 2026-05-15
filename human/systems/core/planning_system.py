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
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from space.space_component import SpaceComponent


class PlanningSystem(System):
    """
    把意图转换为行为序列
    """

    EXPLORE_RADIUS = 20  # 探索半径

    def update(self, world: World, dt):
        for entity, (intent, task, action, space) in world.get_components(
            IntentComponent, TaskComponent, ActionComponent, SpaceComponent
        ):
            
            intent: IntentComponent
            task: TaskComponent
            action: ActionComponent
            space: SpaceComponent

            # 已有任务且正在执行就不重复规划
            if action.action_queue or action.current_action != ActionType.IDLE:
                continue

            if intent.intent == IntentType.EAT:
                task.task = TaskType.FIND_FOOD
                task.status = TaskStatus.RUNNING

                action.action_queue = [
                    ActionType.SEARCH,
                    ActionType.MOVE_TO,
                    ActionType.PICKUP,
                    ActionType.EAT
                ]

            elif intent.intent == IntentType.DRINK:
                task.task = TaskType.DRINK_WATER
                task.status = TaskStatus.RUNNING

                action.action_queue = [
                    ActionType.SEARCH,
                    ActionType.MOVE_TO,
                    ActionType.DRINK
                ]

            elif intent.intent == IntentType.SLEEP:
                task.task = TaskType.SLEEP
                task.status = TaskStatus.RUNNING

                action.action_queue = [
                    ActionType.MOVE_TO,
                    ActionType.SLEEP
                ]

            elif intent.intent == IntentType.EXPLORE:
                task.task = TaskType.EXPLORE
                task.status = TaskStatus.RUNNING

                # 随机选择一个探索目标
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