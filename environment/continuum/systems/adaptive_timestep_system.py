#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自适应时间步长系统 — 数值稳定性控制

v4.0 实现 — Phase 4

物理模型:
    1. 变化检测: 监测每个单元格的变化量
    2. 步长调整: 变化过大时自动减小 dt
    3. 子步进: 一个大步长拆分为多个子步
    4. 守恒验证: 每个子步后验证守恒性

参数:
    MAX_CHANGE_TEMP = 2.0°C (最大单步温度变化)
    MAX_CHANGE_HUMID = 0.05 (最大单步湿度变化)
    MAX_CHANGE_MOIST = 0.05 (最大单步水分变化)
    MIN_DT = 0.01 h (最小时间步长)
    MAX_SUBSTEPS = 10 (最大子步数)

实现细节:
    - 作为包装器包裹其他连续统系统
    - 每个子步后拍摄快照并验证稳定性
    - 不稳定时递归细分并重试
    - 与 EnvironmentalContinuumSystem 集成

与其他模块的关系:
    - continuum/: 控制所有处理器的执行步长
    - 所有环境系统: 受自适应步长影响

版本: v4.0
"""

import logging
import math
from typing import Dict, List, Optional

from core.system import System
from core.world import World
from core.entity import Entity

from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

from environment.continuum.continuum_utils import (
    ConservationSnapshot,
    take_conservation_snapshot,
    check_conservation,
)

logger = logging.getLogger(__name__)


class AdaptiveTimestepSystem(System):
    """
    自适应时间步长系统

    监测环境变化，自动调整时间步长以确保数值稳定:
    1. 计算每个单元格的变化量
    2. 如果变化超过阈值，减小 dt 并重试
    3. 使用子步进完成大时间步长

    在管线中应作为最外层包装器，
    包裹 EnvironmentalContinuumSystem 和其他连续统系统。
    """

    tick_interval = 1  # 每帧执行 (作为包装器)

    # 变化阈值
    MAX_CHANGE_TEMP = 2.0     # 最大温度变化 (°C)
    MAX_CHANGE_HUMID = 0.05   # 最大湿度变化
    MAX_CHANGE_MOIST = 0.05   # 最大水分变化
    MAX_CHANGE_NUTRIENT = 5.0 # 最大养分变化 (mg/kg)

    # 步长限制
    MIN_DT = 0.01    # 最小时间步长 (h)
    MAX_SUBSTEPS = 10  # 最大子步数

    def __init__(self, wrapped_systems: List[System] = None):
        super().__init__()
        self.wrapped_systems = wrapped_systems or []

    def update(self, world: World, dt: float) -> None:
        """自适应更新

        流程:
            1. 计算建议子步数
            2. 执行子步
            3. 每个子步后验证稳定性
            4. 必要时进一步细分
        """
        if dt <= 0 or not self.wrapped_systems:
            return

        # 计算建议子步数
        n_substeps = self._compute_substeps(world, dt)
        sub_dt = dt / n_substeps

        # 执行子步
        for i in range(n_substeps):
            # 拍摄前快照
            before = self._take_snapshot(world)
            before_conservation = take_conservation_snapshot(
                self._build_cache(world)
            )

            # 执行所有包裹的系统
            for system in self.wrapped_systems:
                if hasattr(system, 'update'):
                    system.update(world, sub_dt)

            # 检查稳定性
            if not self._check_stability(world, before):
                # 不稳定，进一步细分
                logger.warning(f"Instability detected at step {i+1}/{n_substeps}, subdividing")
                self._subdivide_and_retry(world, sub_dt)
                continue

            # 检查守恒性
            after_conservation = take_conservation_snapshot(
                self._build_cache(world)
            )
            violation = check_conservation(
                before_conservation, after_conservation, tolerance=1e-6
            )
            if violation:
                logger.warning(f"Conservation violation at step {i+1}/{n_substeps}: {violation}")

    def _compute_substeps(self, world: World, dt: float) -> int:
        """计算建议子步数

        基于当前环境变化率估计:
        - 温度梯度大 → 需要更多子步
        - 风速大 → 需要更多子步
        - 湿度梯度大 → 需要更多子步
        """
        max_rate = 0.0

        for entity, (env,) in world.get_components(EnvironmentComponent):
            if env is None:
                continue

            # 基于当前梯度和扩散系数估计
            # 温度梯度作为代理
            temp_rate = abs(env.air_temperature) / 100.0  # 归一化
            wind_rate = env.wind_speed / 10.0  # 归一化
            humid_rate = abs(env.air_humidity - 0.5) * 2.0  # 归一化

            max_rate = max(max_rate, temp_rate + wind_rate + humid_rate)

        if max_rate <= 0:
            return 1

        # 计算需要的子步数
        n_substeps = int(math.ceil(max_rate * dt))
        n_substeps = max(1, min(n_substeps, self.MAX_SUBSTEPS))

        return n_substeps

    def _take_snapshot(self, world: World) -> Dict[int, Dict[str, float]]:
        """拍摄环境状态快照

        记录每个环境实体的关键状态，用于后续稳定性检查。
        """
        snapshot = {}
        for entity, (env,) in world.get_components(EnvironmentComponent):
            if env is None:
                continue
            snapshot[entity.id] = {
                'temperature': env.air_temperature,
                'humidity': env.air_humidity,
                'moisture': env.soil_moisture,
                'nitrogen': env.nitrogen,
                'phosphorus': env.phosphorus,
                'potassium': env.potassium,
            }
        return snapshot

    def _check_stability(self, world: World, before: Dict) -> bool:
        """检查稳定性

        比较当前状态与快照，检查变化是否超过阈值。
        """
        for entity, (env,) in world.get_components(EnvironmentComponent):
            if env is None or entity.id not in before:
                continue

            prev = before[entity.id]

            # 检查温度变化
            if abs(env.air_temperature - prev['temperature']) > self.MAX_CHANGE_TEMP:
                return False

            # 检查湿度变化
            if abs(env.air_humidity - prev['humidity']) > self.MAX_CHANGE_HUMID:
                return False

            # 检查水分变化
            if abs(env.soil_moisture - prev['moisture']) > self.MAX_CHANGE_MOIST:
                return False

            # 检查养分变化
            if abs(env.nitrogen - prev['nitrogen']) > self.MAX_CHANGE_NUTRIENT:
                return False
            if abs(env.phosphorus - prev['phosphorus']) > self.MAX_CHANGE_NUTRIENT:
                return False
            if abs(env.potassium - prev['potassium']) > self.MAX_CHANGE_NUTRIENT:
                return False

        return True

    def _subdivide_and_retry(self, world: World, dt: float) -> None:
        """进一步细分并重试

        当检测到不稳定时，将时间步长减半并重试。
        如果仍然不稳定，继续递归细分直到达到最小步长。
        """
        sub_dt = dt / 2.0

        if sub_dt < self.MIN_DT:
            logger.warning(f"Cannot subdivide further: dt={sub_dt} < MIN_DT={self.MIN_DT}")
            return

        # 递归细分
        for i in range(2):
            before = self._take_snapshot(world)

            for system in self.wrapped_systems:
                if hasattr(system, 'update'):
                    system.update(world, sub_dt)

            if not self._check_stability(world, before):
                self._subdivide_and_retry(world, sub_dt)

    def _build_cache(self, world: World):
        """构建缓存用于守恒检查"""
        from environment.continuum.continuum_utils import ContinuumCache
        grid = {}
        for entity, (space,) in world.get_components(SpaceComponent):
            if space is None:
                continue
            key = (int(space.x), int(space.y))
            grid[key] = entity
        return ContinuumCache.build(world, grid)

    def add_system(self, system: System) -> None:
        """添加被包裹的系统"""
        self.wrapped_systems.append(system)

    def remove_system(self, system_type: type) -> bool:
        """移除被包裹的系统"""
        for i, sys in enumerate(self.wrapped_systems):
            if isinstance(sys, system_type):
                self.wrapped_systems.pop(i)
                return True
        return False