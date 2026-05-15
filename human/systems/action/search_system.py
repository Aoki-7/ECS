#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:search_system.py
@说明:搜索系统
@时间:2026/04/13
@作者:AI Assistant
@版本:2.0
'''

import math
import random

from core.system import System
from core.world import World

from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.abilities.search_component import SearchComponent
from human.components.abilities.vision_component import VisionComponent
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

from resource.food.components.food_component import FoodComponent
from resource.water.components.water_component import WaterComponent


class SearchSystem(System):
    """
    SEARCH 行为系统。
    依赖 VisionComponent 将视野内实体反馈到行动目标。
    
    当视野内无目标时，尝试随机移动以扩大搜索范围。
    """

    def update(self, world: World, dt: float):
        for _, (action, vision, search, task, space) in world.get_components(
            ActionComponent,
            VisionComponent,
            SearchComponent,
            TaskComponent,
            SpaceComponent,
        ):
            action: ActionComponent
            vision: VisionComponent
            search: SearchComponent
            task: TaskComponent
            space: SpaceComponent

            if action.current_action != ActionType.SEARCH:
                continue

            target_component = self._resolve_target_component(task)

            if target_component is None:
                self._fail_search(action, task, search)
                continue

            if search.target_component is None:
                search.target_component = target_component

            # 在视野范围内搜索目标
            nearest_entity = None
            nearest_distance = float("inf")
            nearest_pos = None

            for candidate in vision.entities:
                if candidate is None:
                    continue

                target_comp = world.get_component(candidate, target_component)
                if target_comp is None:
                    continue

                target_space = world.get_component(candidate, SpaceComponent)
                if target_space is None:
                    continue

                dx = target_space.x - space.x
                dy = target_space.y - space.y
                dist = math.hypot(dx, dy)
                if dist < nearest_distance:
                    nearest_distance = dist
                    nearest_entity = candidate
                    nearest_pos = (target_space.x, target_space.y)

            if nearest_entity is not None:
                # 找到目标了！设置移动目标
                action.target_entity = nearest_entity.id
                action.target_pos = nearest_pos
                action.current_action = ActionType.MOVE_TO
                action.progress = 0.0
                action.status = ActionStatus.RUNNING
                task.status = TaskStatus.RUNNING
                search.result_entity = nearest_entity.id
            else:
                # 视野内无目标 → 随机走一步扩大搜索范围
                roam_x = space.x + random.randint(-3, 3)
                roam_y = space.y + random.randint(-3, 3)
                roam_x = max(0, min(99, roam_x))
                roam_y = max(0, min(99, roam_y))
                
                action.target_pos = (roam_x, roam_y)
                action.current_action = ActionType.MOVE_TO
                action.progress = 0.0
                action.status = ActionStatus.RUNNING
                search.result_entity = None

    def _resolve_target_component(self, task: TaskComponent):
        """根据当前任务类型解析需要搜索的目标组件类型"""
        if task.task == TaskType.FIND_FOOD:
            return FoodComponent
        elif task.task == TaskType.DRINK_WATER:
            return WaterComponent
        return None

    def _fail_search(self, action: ActionComponent, task: TaskComponent, search: SearchComponent):
        """失败处理：只重置当前动作，保留队列"""
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.FAILED
        action.progress = 0.0
        task.status = TaskStatus.FAILED
        search.result_entity = None
