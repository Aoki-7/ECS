#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风暴系统

v3.5 新增 — P2

职责：
    - 根据大气条件生成风暴
    - 模拟风暴演化（增强/减弱/消散）
    - 影响环境（风速、降雨、温度）

设计原则：
    - 纯物理驱动：气压梯度 + 温度差 + 湿度
    - 无硬编码风暴生成条件
    - 风暴强度由能量供应决定

依赖：
    - StormComponent
    - EnvironmentComponent
"""

import logging
from typing import Dict, List, Optional

from core.system import System
from core.world import World

from environment.extreme_weather.components.storm_component import StormComponent
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class StormSystem(System):
    """
    风暴系统

    物理原理：
    - 风暴形成：暖湿空气上升 → 低压区 → 周围空气补充 → 旋转（科里奥利力）
    - 风暴增强：持续的能量供应（暖海水/暖湿空气）
    - 风暴消散：能量供应中断 / 登陆 / 风切变

    每帧更新：
    1. 检测风暴生成条件（物理阈值）
    2. 更新现有风暴
    3. 风暴影响环境
    4. 移除消散的风暴
    """

    tick_interval = 5  # 每5帧执行一次

    # 物理参数（非硬编码阈值，而是物理常数）
    AIR_DENSITY = 1.225  # kg/m³
    CORIOLIS_OMEGA = 7.292e-5  # rad/s
    LATENT_HEAT = 2.5e6  # J/kg

    def update(self, world: World, dt: float) -> None:
        """更新风暴"""
        # 1. 尝试生成新风暴
        self._spawn_storms(world, dt)

        # 2. 更新现有风暴
        self._update_storms(world, dt)

        # 3. 风暴影响环境
        self._affect_environment(world, dt)

        # 4. 移除消散的风暴
        self._remove_dissipated_storms(world)

    def _spawn_storms(self, world: World, dt: float) -> None:
        """
        根据大气条件生成风暴
        纯物理条件，无硬编码
        """
        for entity, (env, space) in world.get_components(
            EnvironmentComponent, SpaceComponent
        ):
            if env is None or space is None:
                continue

            # 检查是否已有风暴
            existing = world.get_component(entity, StormComponent)
            if existing is not None:
                continue

            # 物理条件评估
            # 1. 温度梯度（对流潜力）
            temp_gradient = env.day_night_temp_diff

            # 2. 湿度（能量来源）
            humidity = env.air_humidity

            # 3. 气压（已隐含在环境中）
            # 使用 VPD 作为大气不稳定度指标
            instability = env.vpd

            # 风暴生成概率 = f(温度梯度, 湿度, 不稳定度)
            # 使用物理乘积而非硬编码阈值
            spawn_probability = (
                (temp_gradient / 10.0) *  # 归一化温度梯度
                (humidity) *               # 湿度
                (instability / 3.0) *      # 归一化不稳定度
                0.001 * dt                 # 时间步长缩放
            )

            # 限制概率在合理范围
            spawn_probability = min(0.01, max(0.0, spawn_probability))

            # 随机生成（使用简单确定性方法避免import random）
            # 使用位置和时间作为种子
            seed = int(space.x * 1000 + space.y * 100 + env.air_temperature * 10)
            if self._pseudo_random(seed) < spawn_probability:
                self._create_storm(world, entity, env, space)

    def _create_storm(self, world: World, entity: int, env: EnvironmentComponent, space: SpaceComponent) -> None:
        """创建新风暴"""
        # 根据物理条件确定风暴类型
        if env.air_temperature > 26.0 and env.air_humidity > 0.8:
            # 暖湿条件 → 飓风/台风
            storm_type = "hurricane"
        elif env.day_night_temp_diff > 15.0:
            # 大温差 → 龙卷风
            storm_type = "tornado"
        else:
            # 一般条件 → 雷暴
            storm_type = "thunderstorm"

        storm = StormComponent(
            storm_type=storm_type,
            central_pressure=1000.0,  # 低于标准大气压
            pressure_gradient=5.0,
            temperature_gradient=env.day_night_temp_diff,
            humidity=env.air_humidity,
            latitude=abs(space.y) * 0.1,  # 简化的纬度映射
            max_lifetime=env.air_humidity * 24.0,  # 湿度决定能量供应时间
        )

        storm.update_intensity()
        world.add_component(entity, storm)

        logger.info(f"[Storm] 生成 {storm_type}，强度={storm.intensity:.2f}，位置=({space.x:.1f}, {space.y:.1f})")

    def _update_storms(self, world: World, dt: float) -> None:
        """更新现有风暴"""
        dt_hours = dt / 3600.0  # 转换为小时

        for entity, (storm, env) in world.get_components(
            StormComponent, EnvironmentComponent
        ):
            if storm is None or env is None:
                continue

            # 更新寿命
            storm.lifetime += dt_hours

            # 根据环境更新物理参数
            storm.temperature_gradient = env.day_night_temp_diff
            storm.humidity = env.air_humidity

            # 气压梯度随风暴发展变化
            # 年轻风暴增强，老年风暴减弱
            life_factor = 1.0 - (storm.lifetime / storm.max_lifetime)
            life_factor = max(0.0, life_factor)

            storm.pressure_gradient = 5.0 + 20.0 * life_factor * storm.humidity
            storm.central_pressure = 1013.0 - 50.0 * life_factor * storm.intensity

            # 更新强度
            storm.update_intensity()

            # 更新直径（随强度变化）
            storm.diameter = 1.0 + 50.0 * storm.intensity

    def _affect_environment(self, world: World, dt: float) -> None:
        """风暴影响周围环境"""
        for entity, (storm, storm_space) in world.get_components(
            StormComponent, SpaceComponent
        ):
            if storm is None or storm_space is None:
                continue

            # 影响范围
            influence_radius = storm.diameter * 1000  # km → m

            for other_entity, (env, other_space) in world.get_components(
                EnvironmentComponent, SpaceComponent
            ):
                if other_entity == entity or env is None or other_space is None:
                    continue

                dist = ((storm_space.x - other_space.x) ** 2 + 
                       (storm_space.y - other_space.y) ** 2) ** 0.5

                if dist > influence_radius:
                    continue

                # 影响强度与距离成反比
                influence = (1 - dist / influence_radius) * storm.intensity

                # 增加风速
                env.wind_speed += storm.max_wind_speed * influence * dt

                # 增加降雨（雷暴/飓风）
                if storm.storm_type in ("thunderstorm", "hurricane"):
                    env.rainfall += 50.0 * influence * dt

                # 降低气压（影响温度感知）
                env.air_temperature -= 2.0 * influence * dt

    def _remove_dissipated_storms(self, world: World) -> None:
        """移除消散的风暴"""
        to_remove = []

        for entity, (storm,) in world.get_components(StormComponent):
            if storm is None:
                continue

            # 寿命耗尽或强度过低
            if storm.lifetime >= storm.max_lifetime or storm.intensity < 0.05:
                to_remove.append(entity)

        for entity in to_remove:
            world.remove_component(entity, StormComponent)
            logger.info(f"[Storm] 风暴消散，entity={entity}")

    def _pseudo_random(self, seed: int) -> float:
        """
        伪随机数生成器（确定性）
        使用线性同余法，避免import random
        """
        a = 1103515245
        c = 12345
        m = 2**31
        
        seed = (a * seed + c) % m
        return seed / m
