#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复杂协作任务系统：支持多个人类协作完成复杂任务
"""
import logging
import random
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from core.system import System
from core.world import World
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent
from space.space_component import SpaceComponent
from civilization.settlement.components.settlement_component import SettlementComponent, SettlementType
from human.rl.action_primitives import ActionPrimitive, ActionPrimitiveType, get_action_primitive

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """任务类型"""
    BUILD_SETTLEMENT = auto()  # 建造定居点
    DEFEND_SETTLEMENT = auto() # 防御定居点
    GATHER_RESOURCES = auto()  # 采集资源
    HUNT_ANIMAL = auto()       # 狩猎动物
    EXPLORE_AREA = auto()      # 探索区域
    BUILD_STRUCTURE = auto()   # 建造建筑
    FARM_LAND = auto()         # 耕种土地
    MINE_ORE = auto()          # 开采矿石

@dataclass
class ComplexTask:
    """复杂任务：需要多个人类协作完成"""
    task_id: int
    task_type: TaskType
    target_position: Tuple[float, float]
    required_workers: int = 3
    current_workers: List[int] = field(default_factory=list)
    progress: float = 0.0  # 0.0 ~ 1.0
    is_complete: bool = False
    is_failed: bool = False
    priority: float = 1.0
    required_resources: Dict[str, float] = field(default_factory=dict)
    duration: float = 100.0  # 任务持续时间

class ComplexTaskSystem(System):
    """复杂任务系统：管理多个人类协作完成复杂任务"""
    tick_interval = 5  # 每5帧更新一次

    def __init__(self):
        self.tasks: Dict[int, ComplexTask] = {}
        self.next_task_id = 0
        self.entity_tasks: Dict[int, int] = {}  # 实体ID -> 任务ID

    def update(self, world: World, dt: float):
        """更新复杂任务系统"""
        # 1. 生成新任务
        self._generate_tasks(world)

        # 2. 分配任务给人类
        self._assign_tasks(world)

        # 3. 更新任务进度
        self._update_task_progress(world, dt)

    def _generate_tasks(self, world: World):
        """生成新任务"""
        # 随机生成建造定居点任务
        if random.random() < 0.01 and len(self.tasks) < 5:
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            task = ComplexTask(
                task_id=self.next_task_id,
                task_type=TaskType.BUILD_SETTLEMENT,
                target_position=(x, y),
                required_workers=5,
                required_resources={"wood": 20.0, "stone": 10.0},
                duration=200.0
            )
            self.tasks[task.task_id] = task
            self.next_task_id += 1
            logger.info(f"[ComplexTask] 生成新任务: 建造定居点 at ({x:.1f}, {y:.1f})")

        # 随机生成防御任务
        if random.random() < 0.005 and len(self.tasks) < 5:
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            task = ComplexTask(
                task_id=self.next_task_id,
                task_type=TaskType.DEFEND_SETTLEMENT,
                target_position=(x, y),
                required_workers=3,
                duration=100.0
            )
            self.tasks[task.task_id] = task
            self.next_task_id += 1
            logger.info(f"[ComplexTask] 生成新任务: 防御定居点 at ({x:.1f}, {y:.1f})")

    def _assign_tasks(self, world: World):
        """分配任务给人类"""
        # 获取所有空闲的人类
        idle_humans = []
        for e, (human, intent) in world.get_components(HumanComponent, IntentComponent):
            if e.id not in self.entity_tasks and intent.intent.name == "IDLE":
                idle_humans.append(e.id)

        # 分配任务
        for task in self.tasks.values():
            if task.is_complete or task.is_failed:
                continue
            if len(task.current_workers) >= task.required_workers:
                continue
            # 找到最近的人类
            nearest_humans = self._find_nearest_humans(world, task.target_position, idle_humans, task.required_workers - len(task.current_workers))
            for human_id in nearest_humans:
                task.current_workers.append(human_id)
                self.entity_tasks[human_id] = task.task_id
                idle_humans.remove(human_id)
                logger.info(f"[ComplexTask] 分配任务{task.task_id}给实体{human_id}")

    def _update_task_progress(self, world: World, dt: float):
        """更新任务进度"""
        for task in list(self.tasks.values()):
            if task.is_complete or task.is_failed:
                continue
            # 检查是否有足够的工人在工作
            active_workers = 0
            for worker_id in task.current_workers:
                # 检查工人是否在任务位置附近
                pos = world.get_component(worker_id, SpaceComponent)
                if pos:
                    distance = ((pos.x - task.target_position[0])**2 + (pos.y - task.target_position[1])**2)**0.5
                    if distance <= 10.0:
                        active_workers += 1

            # 更新进度
            if active_workers > 0:
                task.progress += dt / task.duration * active_workers / task.required_workers
                if task.progress >= 1.0:
                    task.is_complete = True
                    logger.info(f"[ComplexTask] 任务{task.task_id}完成！")
                    # 清理任务
                    for worker_id in task.current_workers:
                        if worker_id in self.entity_tasks:
                            del self.entity_tasks[worker_id]
                    del self.tasks[task.task_id]

    def _find_nearest_humans(self, world: World, position: Tuple[float, float], human_ids: List[int], count: int) -> List[int]:
        """查找最近的人类"""
        distances = []
        for human_id in human_ids:
            pos = world.get_component(human_id, SpaceComponent)
            if pos:
                distance = ((pos.x - position[0])**2 + (pos.y - position[1])**2)**0.5
                distances.append((human_id, distance))
        distances.sort(key=lambda x: x[1])
        return [human_id for human_id, _ in distances[:count]]

    def get_task_info(self, task_id: int) -> Optional[ComplexTask]:
        """获取任务信息"""
        return self.tasks.get(task_id)

    def get_entity_task(self, entity_id: int) -> Optional[ComplexTask]:
        """获取实体的任务"""
        task_id = self.entity_tasks.get(entity_id)
        return self.tasks.get(task_id) if task_id is not None else None
