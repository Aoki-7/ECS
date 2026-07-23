#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁徙系统

v3.6 新增 — P0

职责：
    - 根据环境条件驱动动物迁徙
    - 春季北迁、秋季南迁
    - 能量管理、路线规划

设计原则：
    - 纯物理量驱动：温度、光周期、食物
    - 无硬编码迁徙时间，由环境自发决定
    - 能量约束：迁徙消耗能量，需觅食补充

依赖：
    - MigrationComponent
    - EnvironmentComponent
    - SpaceComponent
    - SeasonComponent
"""

import logging
from typing import Dict, List, Optional, Tuple

from core.system import System
from core.world import World

from biology.organisms.animal.migration.components.migration_component import MigrationComponent
from environment.environment_component import EnvironmentComponent
from environment.season.season_component import SeasonComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class MigrationSystem(System):
    """
    迁徙系统

    物理原理：
    - 春季：温度↑ + 日照↑ → 北迁到繁殖地
    - 秋季：温度↓ + 日照↓ → 南迁到越冬地
    - 能量：迁徙消耗能量，食物补充能量
    - 路线：基于繁殖地/越冬地的直线路径

    每帧更新：
    1. 检查迁徙触发条件
    2. 更新迁徙中动物的位置
    3. 检查到达条件
    4. 能量管理
    """

    tick_interval = 2  # 每2帧执行一次（迁徙需要较频繁更新）

    # 物理参数
    ENERGY_COST_PER_DISTANCE = 0.001  # 每单位距离能量消耗
    ENERGY_RECOVERY_RATE = 0.01       # 觅食能量恢复速率
    MIGRATION_SPEED_BASE = 2.0        # 基础迁徙速度

    def update(self, world: World, dt: float) -> None:
        """更新迁徙"""
        # 1. 检查迁徙触发
        self._check_departure_triggers(world, dt)

        # 2. 更新迁徙中动物
        self._update_migrating_animals(world, dt)

        # 3. 检查到达
        self._check_arrivals(world, dt)

        # 4. 能量管理
        self._manage_energy(world, dt)

    def _check_departure_triggers(self, world: World, dt: float) -> None:
        """检查迁徙触发条件"""
        for entity, (migration, env, space) in world.get_components(
            MigrationComponent, EnvironmentComponent, SpaceComponent
        ):
            if migration is None or not migration.is_migratory:
                continue

            if migration.migration_status != "resident":
                continue

            # 获取季节信息（从 year_progress 推导）
            season = world.get_component(entity, SeasonComponent)
            if season:
                # 将 year_progress 转换为季节
                # year_length_hours = 360*24，每季节约 90 天
                day_of_year = season.year_progress / 24.0
                if day_of_year < 90:
                    season_name = "spring"
                elif day_of_year < 180:
                    season_name = "summer"
                elif day_of_year < 270:
                    season_name = "autumn"
                else:
                    season_name = "winter"
            else:
                season_name = ""

            # 春季北迁（繁殖地）
            if season_name in ("spring", "summer"):
                if migration.should_depart_spring(env.air_temperature, env.photoperiod):
                    self._start_migration(world, entity, migration, space, "north")

            # 秋季南迁（越冬地）
            elif season_name in ("autumn", "winter"):
                if migration.should_depart_autumn(env.air_temperature, env.photoperiod):
                    self._start_migration(world, entity, migration, space, "south")

    def _start_migration(self, world: World, entity: int,
                         migration: MigrationComponent,
                         space: SpaceComponent,
                         direction: str) -> None:
        """开始迁徙"""
        if direction == "north":
            migration.current_target = migration.breeding_ground
        else:
            migration.current_target = migration.wintering_ground

        migration.migration_status = "migrating"

        # 生成简单路线（直线）
        if migration.current_target:
            migration.migration_route = [
                (space.x, space.y),
                migration.current_target
            ]

        logger.info(f"[Migration] entity={entity} 开始{direction}迁，目标={migration.current_target}")

    def _update_migrating_animals(self, world: World, dt: float) -> None:
        """更新迁徙中动物的位置"""
        for entity, (migration, space) in world.get_components(
            MigrationComponent, SpaceComponent
        ):
            if migration is None or space is None:
                continue

            if migration.migration_status != "migrating":
                continue

            if migration.current_target is None:
                continue

            # 计算移动方向
            target_x, target_y = migration.current_target
            dx = target_x - space.x
            dy = target_y - space.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance < 1.0:
                # 接近目标，直接到达
                space.x = target_x
                space.y = target_y
                migration.migration_status = "arrived"
                continue

            # 移动
            speed = migration.migration_speed * self.MIGRATION_SPEED_BASE * dt
            move_ratio = min(1.0, speed / distance)

            space.x += dx * move_ratio
            space.y += dy * move_ratio

            # 消耗能量
            energy_cost = distance * self.ENERGY_COST_PER_DISTANCE * move_ratio
            migration.energy_reserve = max(0.0, migration.energy_reserve - energy_cost)

            # 能量耗尽则停止
            if migration.energy_reserve <= 0.05:
                migration.migration_status = "resident"
                logger.warning(f"[Migration] entity={entity} 能量耗尽，停止迁徙")

    def _check_arrivals(self, world: World, dt: float) -> None:
        """检查是否到达目标"""
        for entity, (migration, env) in world.get_components(
            MigrationComponent, EnvironmentComponent
        ):
            if migration is None or migration.migration_status != "arrived":
                continue

            # 检查温度是否适宜
            if migration.can_arrive(env.air_temperature):
                migration.migration_status = "resident"
                migration.current_target = None
                logger.info(f"[Migration] entity={entity} 到达目标，开始定居")

    def _manage_energy(self, world: World, dt: float) -> None:
        """能量管理"""
        for entity, (migration, env) in world.get_components(
            MigrationComponent, EnvironmentComponent
        ):
            if migration is None:
                continue

            # 定居状态可以恢复能量（觅食）
            if migration.migration_status == "resident":
                # 食物可用性影响恢复速度
                food_availability = env.soil_moisture * 0.5 + env.air_humidity * 0.5
                recovery = self.ENERGY_RECOVERY_RATE * food_availability * dt
                migration.energy_reserve = min(1.0, migration.energy_reserve + recovery)