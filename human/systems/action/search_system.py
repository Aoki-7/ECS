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
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

from resource.food.components.food_component import FoodComponent
from resource.water.components.water_component import WaterComponent
from human.components.basic.human_component import HumanComponent


class SearchSystem(System):
    """
    SEARCH 行为系统。
    依赖 VisionComponent 将视野内实体反馈到行动目标。
    
    当视野内无目标时，尝试随机移动以扩大搜索范围。
    """

    def update(self, world: World, dt: float):
        for entity, (action, vision, search, task, space) in world.get_components(
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

            for eid in vision.entity_ids:
                candidate = world.query_entity(eid)
                if candidate is None or not candidate.is_alive():
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
                # 找到目标了！
                action.target_entity = nearest_entity.id
                action.target_pos = nearest_pos
                action.current_action = ActionType.MOVE_TO
                action.progress = 0.0
                action.status = ActionStatus.RUNNING
                task.status = TaskStatus.RUNNING
                search.result_entity = nearest_entity.id
            else:
                # 视野内无目标，优先查询记忆中的地点
                found_memory = False
                memory = world.get_component(entity, MemoryComponent)
                if memory:
                    if task.task == TaskType.DRINK_WATER:
                        mem_pos = memory.find_best_place_by_type("water_source")
                        if mem_pos:
                            action.target_pos = mem_pos
                            action.current_action = ActionType.MOVE_TO
                            action.progress = 0.0
                            action.status = ActionStatus.RUNNING
                            task.status = TaskStatus.RUNNING
                            search.result_entity = None
                            found_memory = True
                    elif task.task == TaskType.FIND_FOOD:
                        mem_pos = memory.find_best_place_by_type("food_source")
                        if mem_pos:
                            action.target_pos = mem_pos
                            action.current_action = ActionType.MOVE_TO
                            action.progress = 0.0
                            action.status = ActionStatus.RUNNING
                            task.status = TaskStatus.RUNNING
                            search.result_entity = None
                            found_memory = True
                
                if not found_memory:
                    # 记忆中也无目标，使用空间索引进行大范围全局搜索
                    space_system = world.get_system(SpaceSystem)
                    found_global = False
                    if space_system is not None:
                        # 对食物和水源都使用 query_radius(30) 全局搜索最近目标
                        if task.task == TaskType.DRINK_WATER:
                            ids = space_system.query_radius(space.x, space.y, 50)
                            best_id = None
                            best_dist = float("inf")
                            for eid in ids:
                                if eid == entity.id:
                                    continue
                                candidate = world.query_entity(eid)
                                if candidate is None:
                                    continue
                                if world.get_component(candidate, WaterComponent) is None:
                                    continue
                                c_space = world.get_component(candidate, SpaceComponent)
                                if c_space is None:
                                    continue
                                d = math.hypot(c_space.x - space.x, c_space.y - space.y)
                                if d < best_dist:
                                    best_dist = d
                                    best_id = candidate
                            # 兜底：遍历所有地面水源
                            if best_id is None:
                                for w_ent, (w_comp, w_space) in world.get_components(WaterComponent, SpaceComponent):
                                    d = math.hypot(w_space.x - space.x, w_space.y - space.y)
                                    if d < best_dist:
                                        best_dist = d
                                        best_id = w_ent
                            if best_id is not None:
                                c_space = world.get_component(best_id, SpaceComponent)
                                action.target_entity = best_id.id
                                action.target_pos = (c_space.x, c_space.y)
                                action.current_action = ActionType.MOVE_TO
                                action.progress = 0.0
                                action.status = ActionStatus.RUNNING
                                task.status = TaskStatus.RUNNING
                                search.result_entity = best_id.id
                                found_global = True

                        elif task.task == TaskType.FIND_FOOD:
                            # 先用空间索引查询半径50内的食物
                            ids = space_system.query_radius(space.x, space.y, 50)
                            best_id = None
                            best_dist = float("inf")
                            for eid in ids:
                                if eid == entity.id:
                                    continue
                                candidate = world.query_entity(eid)
                                if candidate is None:
                                    continue
                                if world.get_component(candidate, FoodComponent) is None:
                                    continue
                                c_space = world.get_component(candidate, SpaceComponent)
                                if c_space is None:
                                    continue
                                d = math.hypot(c_space.x - space.x, c_space.y - space.y)
                                if d < best_dist:
                                    best_dist = d
                                    best_id = candidate
                            # 如果空间索引没找到，直接遍历所有地面食物（兜底，确保不饿死）
                            if best_id is None:
                                for f_ent, (f_comp, f_space) in world.get_components(FoodComponent, SpaceComponent):
                                    d = math.hypot(f_space.x - space.x, f_space.y - space.y)
                                    if d < best_dist:
                                        best_dist = d
                                        best_id = f_ent
                            if best_id is not None:
                                c_space = world.get_component(best_id, SpaceComponent)
                                action.target_entity = best_id.id
                                action.target_pos = (c_space.x, c_space.y)
                                action.current_action = ActionType.MOVE_TO
                                action.progress = 0.0
                                action.status = ActionStatus.RUNNING
                                task.status = TaskStatus.RUNNING
                                search.result_entity = best_id.id
                                found_global = True

                    if not found_global:
                        # 随机向较远位置漫游以扩大搜索范围
                        roam_range = 15
                        roam_x = space.x + random.randint(-roam_range, roam_range)
                        roam_y = space.y + random.randint(-roam_range, roam_range)
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
        elif task.task == TaskType.FIND_PARTNER:
            return HumanComponent
        return None

    def _fail_search(self, action: ActionComponent, task: TaskComponent, search: SearchComponent):
        """失败处理：重置当前动作，移除队列中冗余的搜索/移动步骤，保留最终交互动作"""
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.FAILED
        action.progress = 0.0
        action.target_pos = None
        action.target_entity = None
        # 移除队列前端的 SEARCH/MOVE_TO，保留最终的 EAT/DRINK/SOCIALIZE 等
        while action.action_queue and action.action_queue[0] in (ActionType.SEARCH, ActionType.MOVE_TO):
            action.action_queue.pop(0)
        task.status = TaskStatus.FAILED
        search.result_entity = None
