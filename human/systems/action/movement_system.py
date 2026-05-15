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

from space.space_component import SpaceComponent
from human.components.action.action_component import (
    ActionComponent, ActionType, ActionStatus
)
from human.components.abilities.velocity_component import VelocityComponent


class MovementSystem(System):
    """
    移动系统负责更新同时拥有 SpaceComponent、ActionComponent 和 VelocityComponent 的实体位置。

    仅处理当前动作为 ActionType.MOVE_TO 的实体：
    - 读取 ActionComponent.target_pos 作为目标坐标
    - 按速度和时间增量移动实体
    - 到达时标记 SUCCESS，并将动作置为 IDLE
    - 目标无效时标记 FAILED
    """

    def update(self, world: World, dt):
        """
        更新所有可移动实体的位置。

        Args:
            world: ECS 世界实例
            dt: 本帧时间增量，单位为秒
        """

        for entity, [space, action, velocity] in world.get_components(
            SpaceComponent, ActionComponent, VelocityComponent
        ):
            space: SpaceComponent
            action: ActionComponent
            velocity: VelocityComponent

            if action.current_action != ActionType.MOVE_TO:
                continue

            target = action.target_pos
            if target is None:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                continue

            if isinstance(target, list):
                target = tuple(target)

            try:
                target_x, target_y = target
            except (TypeError, ValueError):
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                continue

            dx = target_x - space.x
            dy = target_y - space.y
            dist = math.hypot(dx, dy)

            if dist < 1e-5:
                space.x = target_x
                space.y = target_y
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.SUCCESS
                action.progress = 1.0
                action.target_pos = None
                continue

            dir_x = dx / dist
            dir_y = dy / dist
            move_dist = velocity.speed * dt

            if move_dist >= dist:
                space.x = target_x
                space.y = target_y
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.SUCCESS
                action.progress = 1.0
                action.target_pos = None
            else:
                space.x += dir_x * move_dist
                space.y += dir_y * move_dist
                new_dx = target_x - space.x
                new_dy = target_y - space.y
                remain = math.hypot(new_dx, new_dy)
                action.progress = 1.0 - (remain / dist)
                action.status = ActionStatus.RUNNING
