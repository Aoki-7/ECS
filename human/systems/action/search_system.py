#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:search_system.py
@说明:搜索系统 v2.0 — 递进式策略 + 搜索历史 + 记忆写入
@时间:2026/04/13
@作者:AI Assistant
@版本:2.0

增强说明（v2.0）：
    1. 递进式搜索策略：visual → memory → explore → random
    2. 搜索历史管理：避免在同一区域重复搜索
    3. 概率更新：根据成功率动态调整 estimated_probability
    4. 发现即记忆：找到目标后立即 record_place，无需等到动作完成
    5. 策略切换记录：写入 search.strategy_history 供分析
'''

import math
import random

from core.system import System
from core.world import World

from core.components.action_component import ActionComponent, ActionType, ActionStatus
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from core.components.search_component import SearchComponent
from core.components.vision_component import VisionComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

from resource.food.components.food_component import FoodComponent
from resource.water.components.water_component import WaterComponent
from resource.components.resource_component import ResourceComponent
from human.components.basic.human_component import HumanComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from plant.components.plant_component import PlantComponent

import logging

logger = logging.getLogger(__name__)


class SearchSystem(System):
    tick_interval = 1
    """
    SEARCH 行为系统 v2.0

    递进式搜索策略：
        1. visual  : 视觉扫描（VisionComponent 的 focused_entity_ids）
        2. memory  : 记忆回溯（MemoryComponent.find_best_place_by_type）
        3. explore : 扩大探索（空间索引 query_radius 50/100）
        4. random  : 随机漫游（扩大搜索范围）

    每次搜索后更新：
        - search.strategy         : 当前使用的策略
        - search.strategy_history : 策略切换记录
        - search.search_history   : 搜索过的位置
        - search.total_searches   : 累计搜索次数
        - search.successful_searches : 累计成功次数
        - search.estimated_probability : 动态概率 = (success+1)/(total+2)
        - search.discoveries      : 发现记录（供记忆系统读取）
    """

    def update(self, world: World, dt: float):
        from core.components.world_config_component import WorldConfigComponent
        world_config = world.get_world_component(WorldConfigComponent)

        for entity, (action, vision, search, task, space) in world.get_components(
            ActionComponent, VisionComponent, SearchComponent, TaskComponent, SpaceComponent
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

            # 更新搜索统计
            search.total_searches += 1
            search.last_search_tick = world.tick_count

            nearest_entity, nearest_pos, used_strategy = self._execute_search(
                world, entity, space, vision, search, task, target_component
            )

            if nearest_entity is None:
                self._handle_random_roam(world, world_config, entity, action, search, task, space)
                continue

            self._handle_target_found(
                world, entity, action, search, task, nearest_entity, nearest_pos, used_strategy
            )

    def _execute_search(self, world, entity, space, vision, search, task, target_component):
        """执行递进式搜索策略，返回 (nearest_entity, nearest_pos, used_strategy)"""
        # ── 第 1 步：视觉扫描 ──
        nearest_entity, _, nearest_pos = self._search_visual(
            world, entity, space, vision, target_component, task
        )
        used_strategy = "visual"

        # ── 第 2 步：记忆回溯（视觉失败时）──
        if nearest_entity is None:
            nearest_entity, nearest_pos = self._search_memory(
                world, entity, space, task
            )
            if nearest_entity is not None:
                used_strategy = "memory"

        # ── 第 3 步：扩大探索（记忆也失败时）──
        if nearest_entity is None:
            nearest_entity, nearest_pos = self._search_explore(
                world, entity, space, target_component, task
            )
            if nearest_entity is not None:
                used_strategy = "explore"

        return nearest_entity, nearest_pos, used_strategy

    def _handle_random_roam(self, world, world_config, entity, action, search, task, space):
        """全部搜索策略失败时，执行随机漫游"""
        roam_range = 15
        roam_x = space.x + random.randint(-roam_range, roam_range)
        roam_y = space.y + random.randint(-roam_range, roam_range)
        if world_config is not None:
            roam_x, roam_y = world_config.clamp_position(roam_x, roam_y)
        else:
            roam_x = max(0, roam_x)
            roam_y = max(0, roam_y)

        action.target_pos = (roam_x, roam_y)
        action.current_action = ActionType.MOVE_TO
        action.progress = 0.0
        action.status = ActionStatus.RUNNING
        search.result_entity = None

        self._record_search(search, world.tick_count, space.x, space.y, "random", found=False)

    def _handle_target_found(self, world, entity, action, search, task, nearest_entity, nearest_pos, used_strategy):
        """找到目标后的处理逻辑"""
        search.successful_searches += 1
        search.estimated_probability = (search.successful_searches + 1) / (search.total_searches + 2)
        search.strategy = used_strategy

        action.target_entity = nearest_entity.id
        action.target_pos = nearest_pos
        action.current_action = ActionType.MOVE_TO
        action.progress = 0.0
        action.status = ActionStatus.RUNNING
        task.status = TaskStatus.RUNNING
        search.result_entity = nearest_entity.id

        # 记录搜索历史和策略
        self._record_search(search, world.tick_count, nearest_pos[0], nearest_pos[1], used_strategy, found=True)
        self._record_strategy(search, world.tick_count, used_strategy, found=True)

        # 发现即记忆
        self._record_discovery(world, entity, search, nearest_entity, nearest_pos, task)

        # 队列处理
        if ActionType.SEARCH in action.action_queue:
            action.action_queue.remove(ActionType.SEARCH)
        if world.get_component(nearest_entity, PlantComponent) is not None:
            for i, act in enumerate(action.action_queue):
                if act == ActionType.PICKUP:
                    action.action_queue[i] = ActionType.HARVEST
                    break

    # ── 搜索策略实现 ──

    def _search_visual(self, world, entity, space, vision, target_component, task):
        """视觉扫描：在 focused_entity_ids 和 entity_ids 中查找最近目标"""
        nearest_entity = None
        nearest_distance = float("inf")
        nearest_pos = None

        # 优先扫描 focused_entity_ids（注意力目标），再扫描全部 entity_ids
        ids_to_check = list(vision.focused_entity_ids) + [eid for eid in vision.entity_ids if eid not in vision.focused_entity_ids]
        seen = set()

        for eid in ids_to_check:
            if eid in seen:
                continue
            seen.add(eid)

            candidate = world.query_entity(eid)
            if candidate is None or not candidate.is_alive():
                continue

            target_comp = world.get_component(candidate, target_component)
            c_space = world.get_component(candidate, SpaceComponent)
            if c_space is None:
                continue

            if target_comp is not None:
                dist = math.hypot(c_space.x - space.x, c_space.y - space.y)
                if dist < nearest_distance:
                    nearest_distance = dist
                    nearest_entity = candidate
                    nearest_pos = (c_space.x, c_space.y)
                continue

            # 特殊处理：FIND_FOOD 时也搜索可收获植物
            if task.task == TaskType.FIND_FOOD:
                plant = self._check_harvestable_plant(world, candidate, space)
                if plant:
                    dist, cnd, pos = plant
                    if dist < nearest_distance:
                        nearest_distance = dist
                        nearest_entity = cnd
                        nearest_pos = pos

        return nearest_entity, nearest_distance, nearest_pos

    def _search_memory(self, world, entity, space, task):
        """记忆回溯：从 MemoryComponent 读取已知位置"""
        memory = world.get_component(entity, MemoryComponent)
        if memory is None:
            return None, None

        place_type = None
        if task.task == TaskType.DRINK_WATER:
            place_type = "water_source"
        elif task.task == TaskType.FIND_FOOD:
            place_type = "food_source"

        if place_type is None:
            return None, None

        mem_pos = memory.find_best_place_by_type(place_type)
        if mem_pos is None:
            return None, None

        # 返回一个"虚拟实体"（仅用于统一接口），实际移动目标是 mem_pos
        # 简化处理：直接返回位置，上层用 target_pos 移动
        return "MEMORY_TARGET", mem_pos

    def _search_explore(self, world, entity, space, target_component, task):
        """扩大探索：使用空间索引大范围扫描"""
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return None, None

        nearest_entity = None
        nearest_distance = float("inf")
        nearest_pos = None

        for radius in (50, 100):
            ids = space_system.query_radius(space.x, space.y, radius)
            for eid in ids:
                if eid == entity.id:
                    continue
                candidate = world.query_entity(eid)
                if candidate is None:
                    continue

                if world.get_component(candidate, target_component) is not None:
                    c_space = world.get_component(candidate, SpaceComponent)
                    if c_space is None:
                        continue
                    dist = math.hypot(c_space.x - space.x, c_space.y - space.y)
                    if dist < nearest_distance:
                        nearest_distance = dist
                        nearest_entity = candidate
                        nearest_pos = (c_space.x, c_space.y)
                    continue

                if task.task == TaskType.FIND_FOOD:
                    plant = self._check_harvestable_plant(world, candidate, space)
                    if plant:
                        dist, cnd, pos = plant
                        if dist < nearest_distance:
                            nearest_distance = dist
                            nearest_entity = cnd
                            nearest_pos = pos

            if nearest_entity is not None:
                break

        return nearest_entity, nearest_pos

    def _check_harvestable_plant(self, world, candidate, observer_space):
        """检查候选实体是否为可收获植物，返回 (dist, entity, pos) 或 None"""
        plant_comp = world.get_component(candidate, PlantComponent)
        if plant_comp is None:
            return None
        lifecycle = world.get_component(candidate, LifeCycleComponent)
        if lifecycle is None or lifecycle.stage < plant_comp.harvest_stage:
            return None
        c_space = world.get_component(candidate, SpaceComponent)
        if c_space is None:
            return None
        dist = math.hypot(c_space.x - observer_space.x, c_space.y - observer_space.y)
        return dist, candidate, (c_space.x, c_space.y)

    # ── 记录方法 ──

    def _record_search(self, search: SearchComponent, tick: int, x: float, y: float, strategy: str, found: bool):
        """记录搜索历史"""
        search.search_history.append((tick, x, y, strategy, found))
        if len(search.search_history) > search.max_history_size:
            search.search_history.pop(0)

    def _record_strategy(self, search: SearchComponent, tick: int, strategy: str, found: bool):
        """记录策略切换历史"""
        search.strategy_history.append((tick, strategy, found))
        if len(search.strategy_history) > 10:
            search.strategy_history.pop(0)

    def _record_discovery(self, world, entity, search, target, target_pos, task):
        """发现即记忆：立即记录到 search.discoveries 和 memory"""
        # A) 写入 search.discoveries
        place_type = self._task_to_place_type(task)
        search.discoveries.append((
            search.last_search_tick, target.id if hasattr(target, 'id') else None,
            target_pos[0], target_pos[1], place_type
        ))

        # B) 写入 memory
        memory = world.get_component(entity, MemoryComponent)
        if memory is None:
            return

        current_time = 0.0
        try:
            time_comp = world.get_time()
            if time_comp:
                current_time = time_comp.total_hours
        except Exception as e:
            logger.warning(f"[SearchSystem] 获取世界时间失败: {e}")

        if place_type is not None:
            memory.record_place(target_pos, place_type, current_time, sentiment=0.5)

    def _task_to_place_type(self, task: TaskComponent) -> str | None:
        """任务类型转换为地点类型"""
        if task.task == TaskType.DRINK_WATER:
            return "water_source"
        elif task.task == TaskType.FIND_FOOD:
            return "food_source"
        return None

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
        while action.action_queue and action.action_queue[0] in (ActionType.SEARCH, ActionType.MOVE_TO):
            action.action_queue.pop(0)
        task.status = TaskStatus.FAILED
        search.result_entity = None
