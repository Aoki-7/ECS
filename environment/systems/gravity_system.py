#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:gravity_system.py
@说明:重力系统

职责：
    1. 从环境组件读取重力配置
    2. 为所有具有 SpaceComponent 的实体应用重力
    3. 更新实体下落速度
    4. 处理终端速度限制
    5. 检测地面碰撞

设计原则：
    - 重力是环境属性，由 EnvironmentComponent/GravityComponent 配置
    - 只影响有 SpaceComponent（位置）的实体
    - 与 SpaceSystem 协作处理空间位置
'''

import logging
from typing import Optional

from core.system import System
from core.world import World
from core.entity import Entity

from environment.components.gravity_component import GravityComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class GravitySystem(System):
    """
    重力系统

    每帧为所有具有 SpaceComponent 的实体应用重力加速度，
    更新其垂直位置。
    """

    tick_interval = 1  # 每帧执行（重力变化快）

    def __init__(self):
        super().__init__()
        self._ground_y = 0.0  # 地面高度（可配置）

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        应用重力到所有实体

        Args:
            world: ECS 世界
            dt: 时间步长（秒）
        """
        # 从环境获取重力配置
        gravity = self._get_gravity(world)
        if gravity is None or not gravity.is_enabled:
            return

        for entity, space in world.get_components(SpaceComponent):
            self._apply_gravity(entity, space, gravity, dt)

    def _get_gravity(self, world: World) -> Optional[GravityComponent]:
        """获取环境重力配置"""
        # 优先从世界实体的 GravityComponent 获取
        world_entity = world.get_world_entity()
        if world_entity:
            comp = world.get_component(world_entity, GravityComponent)
            if comp:
                return comp

        # 回退：从 EnvironmentComponent 获取（如果环境组件有重力字段）
        try:
            from environment.environment_component import EnvironmentComponent
            env = world.get_environment()
            if env and hasattr(env, 'gravity'):
                g = env.gravity
                return GravityComponent(acceleration=g)
        except (ImportError, AttributeError):
            pass

        # 默认重力
        return GravityComponent()

    def _apply_gravity(self, entity: Entity, space: SpaceComponent,
                       gravity: GravityComponent, dt: float) -> None:
        """
        对单个实体应用重力

        Args:
            entity: 实体
            space: 空间组件
            gravity: 重力配置
            dt: 时间步长
        """
        # 计算重力加速度向量
        ax = gravity.direction_x * gravity.acceleration
        ay = gravity.direction_y * gravity.acceleration
        az = gravity.direction_z * gravity.acceleration

        # 更新速度（假设 SpaceComponent 有 velocity 属性）
        if hasattr(space, 'velocity_x'):
            space.velocity_x += ax * dt
        if hasattr(space, 'velocity_y'):
            space.velocity_y += ay * dt
            # 限制终端速度
            if abs(space.velocity_y) > gravity.max_fall_speed:
                space.velocity_y = -gravity.max_fall_speed if space.velocity_y < 0 else gravity.max_fall_speed
        if hasattr(space, 'velocity_z'):
            space.velocity_z += az * dt

        # 更新位置
        if hasattr(space, 'velocity_x'):
            space.x += space.velocity_x * dt
        if hasattr(space, 'velocity_y'):
            space.y += space.velocity_y * dt
        if hasattr(space, 'velocity_z'):
            space.z += space.velocity_z * dt

        # 简单地面碰撞检测
        if hasattr(space, 'y') and space.y < self._ground_y:
            space.y = self._ground_y
            if hasattr(space, 'velocity_y'):
                space.velocity_y = 0.0

    def set_ground_level(self, y: float) -> None:
        """设置地面高度"""
        self._ground_y = y

    def get_ground_level(self) -> float:
        """获取地面高度"""
        return self._ground_y
