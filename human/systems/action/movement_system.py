from human.systems.cognitive.memory_management_system import MemoryManagementSystem
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件: movement_system.py
@说明: 负责 MOVE_TO 执行动作的实体移动逻辑
@时间: 2026/03/13 13:42:20
@作者: Sherry
@版本: 1.2
'''

import math

from core.system import System
from core.world import World
from core.components.world_config_component import WorldConfigComponent
from core.systems.world_config_system import WorldConfigSystem

from space.space_component import SpaceComponent
from human.components.action.action_component import (
    ActionComponent, ActionType, ActionStatus
)
from human.components.abilities.velocity_component import VelocityComponent
from human.components.cognitive.task_component import TaskComponent, TaskType
from human.components.cognitive.memory_component import MemoryComponent


class MovementSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    移动系统负责更新同时拥有 SpaceComponent、ActionComponent 和 VelocityComponent 的实体位置。

    仅处理当前动作为 ActionType.MOVE_TO 的实体：
    - 读取 ActionComponent.target_pos 作为目标坐标
    - 按速度和时间增量移动实体
    - 到达时标记 SUCCESS，并将动作置为 IDLE
    - 目标无效时标记 FAILED
    """

    def update(self, world: World, dt: float):
        """更新所有可移动实体的位置"""
        world_config = WorldConfigSystem.get_world_config(world)
        for entity, [space, action, velocity] in world.get_components(
            SpaceComponent, ActionComponent, VelocityComponent
        ):
            if action.current_action != ActionType.MOVE_TO:
                continue
            self._process_movement(entity, space, action, velocity, world, dt, world_config)

    def _process_movement(self, entity, space, action, velocity, world, dt, world_config=None) -> None:
        """处理单个实体的移动"""
        target = self._validate_target(action.target_pos, world_config)
        if target is None:
            self._fail_movement(action)
            return

        target_x, target_y = target
        dx = target_x - space.x
        dy = target_y - space.y
        dist = math.hypot(dx, dy)

        if dist < 1e-5:
            self._arrive_at_target(space, action, target_x, target_y, world_config)
            return

        dir_x = dx / dist
        dir_y = dy / dist
        move_dist = velocity.speed * dt

        if move_dist >= dist:
            self._complete_movement(space, action, target_x, target_y, entity, world, world_config)
        else:
            self._partial_movement(space, action, target_x, target_y, dir_x, dir_y, move_dist, dist, world_config)

    def _validate_target(self, target, world_config=None):
        """验证并规范化目标位置，并将其限制在世界边界内"""
        if target is None:
            return None
        if isinstance(target, list):
            target = tuple(target)
        try:
            target = tuple(target)
        except (TypeError, ValueError):
            return None
        if world_config is None:
            return target
        return self._clamp_position(world_config, target[0], target[1])

    @staticmethod
    def _clamp_position(world_config, x, y):
        """将坐标限制在世界边界内"""
        if world_config is None:
            return x, y
        return (
            max(0, min(world_config.map_width - 1, x)),
            max(0, min(world_config.map_height - 1, y))
        )
    def _fail_movement(self, action) -> None:
        """标记移动失败"""
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.FAILED
        action.progress = 0.0

    def _arrive_at_target(self, space, action, target_x, target_y, world_config=None) -> None:
        """到达目标位置"""
        space.x, space.y = self._clamp_position(world_config, target_x, target_y)
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.SUCCESS
        action.progress = 1.0
        action.target_pos = None

    def _complete_movement(self, space, action, target_x, target_y, entity, world, world_config=None) -> None:
        """完成移动（到达或超过目标）"""
        space.x, space.y = self._clamp_position(world_config, target_x, target_y)
        space.dirty = True
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.SUCCESS
        action.progress = 1.0
        action.target_pos = None
        self._record_explore_success(entity, world)

    def _partial_movement(self, space, action, target_x, target_y, dir_x, dir_y, move_dist, total_dist, world_config=None) -> None:
        """部分移动（未到达目标）"""
        new_x = round(space.x + dir_x * move_dist)
        new_y = round(space.y + dir_y * move_dist)
        space.x, space.y = self._clamp_position(world_config, new_x, new_y)
        space.dirty = True
        remain = math.hypot(target_x - space.x, target_y - space.y)
        action.progress = 1.0 - (remain / total_dist)
        action.status = ActionStatus.RUNNING

    def _record_explore_success(self, entity, world) -> None:
        """记录探索成功"""
        task = world.get_component(entity, TaskComponent)
        if task and task.task == TaskType.EXPLORE:
            memory = world.get_component(entity, MemoryComponent)
            if memory and hasattr(memory, 'record_success'):
                MemoryManagementSystem.record_success(memory, "explore")
            elif memory and hasattr(memory, 'recent_successes'):
                if isinstance(memory.recent_successes, list):
                    memory.recent_successes.append("explore")
                elif isinstance(memory.recent_successes, dict):
                    memory.recent_successes["explore"] = memory.recent_successes.get("explore", 0) + 1