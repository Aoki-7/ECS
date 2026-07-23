from human.systems.cognitive.memory_management_system import MemoryManagementSystem
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
人类种植系统

处理 ActionType.PLANT 行为：
    1. 检查目标位置是否适合种植
    2. 在目标位置创建植物实体
    3. 记录种植记忆

与 plant 模块的配合：
    调用 PlantFactory.create_plant() 创建新植物实体。
"""

import random

from core.system import System
from core.world import World

from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

import logging

logger = logging.getLogger(__name__)


class PlantingSystem(System):
    tick_interval = 1
    """
    种植系统

    职责：
        1. 处理 PLANT 动作
        2. 在 target_pos 创建植物
        3. 更新记忆
    """

    PLANT_DISTANCE = 3  # 种植距离阈值

    def update(self, world: World, dt: float = 1.0) -> None:
        for entity, (needs, action, task, space) in list(
            world.get_components(
                PhysiologyNeedsComponent,
                ActionComponent,
                TaskComponent,
                SpaceComponent,
            )
        ):
            if action.current_action != ActionType.PLANT:
                continue
            self._process_planting(world, entity, action, task, space)

    def _process_planting(self, world, entity, action, task, space) -> None:
        """处理单个种植行为"""
        target = action.target_pos
        if target is None:
            self._fail(action, task, "无目标位置")
            return

        target_x, target_y = int(target[0]), int(target[1])

        # 距离检查
        dist = abs(space.x - target_x) + abs(space.y - target_y)
        if dist > self.PLANT_DISTANCE:
            self._fail(action, task, f"距离过远 ({dist} > {self.PLANT_DISTANCE})")
            return

        # 检查目标位置是否已有植物
        if self._has_plant_at(world, target_x, target_y):
            self._fail(action, task, "目标位置已有植物")
            return

        # 创建植物
        species = self._create_plant_at(world, target_x, target_y)

        # 记录记忆
        self._record_planting_memory(world, entity, target_x, target_y, species)

        # 标记完成
        action.progress = 1.0
        action.status = ActionStatus.SUCCESS
        task.status = TaskStatus.DONE
        action.target_pos = None

        logger.debug(
            f"[Planting] E{entity.id} 在 ({target_x},{target_y}) 种植了 {species}"
        )

    def _has_plant_at(self, world, target_x: int, target_y: int) -> bool:
        """检查目标位置是否已有植物"""
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return False
        nearby = space_system.query_radius(x=target_x, y=target_y, r=2)
        from biology.organisms.plant.components.plant_component import PlantComponent
        for nid in nearby:
            if world.get_component_by_id(nid, PlantComponent) is not None:
                return True
        return False

    def _create_plant_at(self, world, target_x: int, target_y: int):
        """在指定位置创建植物"""
        from biology.organisms.plant.plant_factory import PlantFactory
        species_list = list(PlantFactory.SPECIES_PRESETS.keys())
        species = random.choice(species_list)
        PlantFactory.create_plant(
            world,
            species=species,
            x=target_x,
            y=target_y,
            variation=0.15,
        )
        return species

    def _record_planting_memory(self, world, entity, target_x: int, target_y: int, species: str) -> None:
        """记录种植记忆"""
        memory = world.get_component(entity, MemoryComponent)
        if memory is None:
            return
        current_time = world.get_time().total_hours
        MemoryManagementSystem.add_event(memory, 
            current_time,
            "planted",
            f"在 ({target_x}, {target_y}) 种植了 {species}",
            impact=0.5,
            location=(target_x, target_y),
        )
        MemoryManagementSystem.record_success(memory, "plant")

    def _fail(self, action: ActionComponent, task: TaskComponent, reason: str) -> None:
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.FAILED
        action.progress = 0.0
        task.status = TaskStatus.FAILED
        logger.debug(f"[Planting] 失败: {reason}")