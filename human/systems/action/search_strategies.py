from human.systems.cognitive.memory_management_system import MemoryManagementSystem
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
搜索策略模块

将 SearchSystem 的搜索策略拆分为独立的策略类，
便于单元测试和策略扩展。
"""

import math
import random
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from core.world import World
from core.entity import Entity

from human.components.action.search_component import SearchComponent
from human.components.perception.vision_component import VisionComponent
from human.components.cognitive.task_component import TaskComponent, TaskType
from space.space_component import SpaceComponent
from biology.components.smell_component import SmellComponent
from biology.systems.smell_diffusion_system import SmellDiffusionSystem
from biology.organisms.plant.components.plant_component import PlantComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from human.components.cognitive.memory_component import MemoryComponent
from space.space_system import SpaceSystem
from resource.food.components.food_component import FoodComponent
from resource.water.components.water_component import WaterComponent
from human.components.basic.human_component import HumanComponent

import logging

logger = logging.getLogger(__name__)


class SearchStrategy(ABC):
    """搜索策略基类"""

    @abstractmethod
    def search(self, world: World, entity: Entity, space: SpaceComponent,
               task: TaskComponent, **kwargs) -> Tuple[Optional[Entity], Optional[Tuple[float, float]], str]:
        """
        执行搜索

        Returns:
            (target_entity, target_pos, strategy_name)
            target_entity 可能为 None（表示未找到）
            target_pos 可能为 None
        """
        pass


class VisualSearchStrategy(SearchStrategy):
    """视觉扫描策略"""

    def search(self, world: World, entity: Entity, space: SpaceComponent,
               task: TaskComponent, **kwargs) -> Tuple[Optional[Entity], Optional[Tuple[float, float]], str]:
        vision = world.get_component(entity, VisionComponent)
        if vision is None:
            return None, None, "visual"

        target_component = kwargs.get('target_component')
        nearest_entity = None
        nearest_distance = float("inf")
        nearest_pos = None

        # 优先扫描 focused_entity_ids，再扫描全部 entity_ids
        ids_to_check = list(vision.focused_entity_ids) + [
            eid for eid in vision.entity_ids if eid not in vision.focused_entity_ids
        ]
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

        return nearest_entity, nearest_pos, "visual"

    def _check_harvestable_plant(self, world, candidate, observer_space):
        """检查候选实体是否为可收获植物"""
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


class SmellSearchStrategy(SearchStrategy):
    """嗅觉感知策略"""

    def search(self, world: World, entity: Entity, space: SpaceComponent,
               task: TaskComponent, **kwargs) -> Tuple[Optional[Entity], Optional[Tuple[float, float]], str]:
        smell = world.get_component(entity, SmellComponent)
        if smell is None:
            return None, None, "smell"

        # 获取气味扩散系统
        smell_system = None
        for sys in world.systems:
            if isinstance(sys, SmellDiffusionSystem):
                smell_system = sys
                break

        if smell_system is None:
            return None, None, "smell"

        # 根据任务类型确定要追踪的气味
        target_scent = None
        if task.task == TaskType.FIND_FOOD:
            target_scent = "food"
        elif task.task == TaskType.DRINK_WATER:
            target_scent = "water"

        if target_scent is None:
            return None, None, "smell"

        # 检测周围气味
        detected = smell_system.get_smell_at(space.x, space.y)
        if target_scent not in detected or detected[target_scent] < 0.1:
            return None, None, "smell"

        # 在周围寻找气味最强的方向
        best_direction = None
        best_intensity = detected.get(target_scent, 0)
        search_radius = int(smell.detection_radius / smell_system.GRID_SIZE)

        for dx in range(-search_radius, search_radius + 1):
            for dy in range(-search_radius, search_radius + 1):
                if dx == 0 and dy == 0:
                    continue
                check_x = space.x + dx * smell_system.GRID_SIZE
                check_y = space.y + dy * smell_system.GRID_SIZE
                nearby_smells = smell_system.get_smell_at(check_x, check_y)
                intensity = nearby_smells.get(target_scent, 0)
                if intensity > best_intensity:
                    best_intensity = intensity
                    best_direction = (check_x, check_y)

        if best_direction is None:
            return None, None, "smell"

        # 在气味最强的方向寻找实际目标
        nearest_entity = None
        nearest_distance = float("inf")
        nearest_pos = None
        target_component = kwargs.get('target_component')

        for eid, (e_space,) in world.get_components(SpaceComponent):
            if eid == entity.id:
                continue
            dist = math.hypot(e_space.x - best_direction[0], e_space.y - best_direction[1])
            if dist < nearest_distance:
                target_comp = world.get_component(world.query_entity(eid), target_component)
                if target_comp is not None:
                    nearest_distance = dist
                    nearest_entity = world.query_entity(eid)
                    nearest_pos = (e_space.x, e_space.y)

        return nearest_entity, nearest_pos, "smell"


class MemorySearchStrategy(SearchStrategy):
    """记忆回溯策略"""

    def search(self, world: World, entity: Entity, space: SpaceComponent,
               task: TaskComponent, **kwargs) -> Tuple[Optional[Entity], Optional[Tuple[float, float]], str]:
        memory = world.get_component(entity, MemoryComponent)
        if memory is None:
            return None, None, "memory"

        place_type = None
        if task.task == TaskType.DRINK_WATER:
            place_type = "water_source"
        elif task.task == TaskType.FIND_FOOD:
            place_type = "food_source"

        if place_type is None:
            return None, None, "memory"

        mem_pos = MemoryManagementSystem.find_best_place_by_type(memory, place_type)
        if mem_pos is None:
            return None, None, "memory"

        # 返回 "MEMORY_TARGET" 作为标记，实际移动目标是 mem_pos
        return "MEMORY_TARGET", mem_pos, "memory"


class ExploreSearchStrategy(SearchStrategy):
    """扩大探索策略"""

    def search(self, world: World, entity: Entity, space: SpaceComponent,
               task: TaskComponent, **kwargs) -> Tuple[Optional[Entity], Optional[Tuple[float, float]], str]:
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return None, None, "explore"

        target_component = kwargs.get('target_component')
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

        return nearest_entity, nearest_pos, "explore"

    def _check_harvestable_plant(self, world, candidate, observer_space):
        """检查候选实体是否为可收获植物"""
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


# 策略注册表
SEARCH_STRATEGIES = [
    VisualSearchStrategy(),
    SmellSearchStrategy(),
    MemorySearchStrategy(),
    ExploreSearchStrategy(),
]