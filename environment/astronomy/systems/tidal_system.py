#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
潮汐系统

v3.5 新增 — P2

职责：
    - 根据天体引力计算潮汐力
    - 影响海洋水位（ TideComponent ）
    - 与月球轨道相位耦合

设计原则：
    - 纯物理驱动：F_tidal = G * M * r / d³
    - 无硬编码潮汐高度，由引力和地形共同决定
    - 支持多个天体（月球、太阳）
"""

import logging
import math
from typing import Dict, List, Tuple

from core.system import System
from core.world import World

from environment.astronomy.components.celestial_body_component import CelestialBodyComponent
from environment.ocean.components.tide_component import TideComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class TidalSystem(System):
    """
    潮汐系统

    物理原理：
    - 潮汐力 ∝ M / d³（质量/距离立方）
    - 高潮发生在天体正上方和正对面
    - 低潮发生在两者之间

    每帧更新：
    1. 计算各天体的潮汐力贡献
    2. 合成总潮汐力
    3. 更新潮汐水位
    4. 推进天体轨道相位
    """

    tick_interval = 10  # 每10帧执行一次

    # 物理常数
    EARTH_RADIUS = 6.371e6  # 地球半径 m
    TIDE_AMPLIFICATION = 1.0e-6  # 潮汐放大系数（将引力转换为水位变化）


    # === 业务方法（从 CelestialBodyComponent 迁移） ===
    @staticmethod
    def tidal_force(body: CelestialBodyComponent) -> float:
        """潮汐力 = M / d³"""
        d = body.distance
        if d <= 0:
            return 0.0
        return body.mass / (d ** 3)

    @staticmethod
    def current_distance(body: CelestialBodyComponent) -> float:
        """当前距离（考虑轨道偏心率）"""
        a = body.distance
        e = body.eccentricity
        theta = body.current_phase
        return a * (1 - e * e) / (1 + e * math.cos(theta))

    @staticmethod
    def get_tidal_force(body: CelestialBodyComponent) -> float:
        """获取潮汐力（兼容旧测试）"""
        return TidalSystem.tidal_force(body)

    @staticmethod
    def advance_orbit(body: CelestialBodyComponent, dt: float = 1.0) -> None:
        """推进轨道"""
        body.phase += body.phase_rate * dt
        body.phase %= (2 * math.pi)
        body.current_phase = body.phase

    @staticmethod
    def advance_phase(body: CelestialBodyComponent, dt: float = 1.0) -> None:
        """推进相位"""
        TidalSystem.advance_orbit(body, dt)

    @staticmethod
    def get_tide_level(body: CelestialBodyComponent) -> float:
        """获取潮汐高度"""
        return TidalSystem.tidal_force(body) * math.sin(body.phase)

    def update(self, world: World, dt: float) -> None:
        """更新潮汐"""
        # 1. 推进天体轨道
        self._advance_orbits(world, dt)

        # 2. 计算潮汐力并更新水位
        self._update_tides(world, dt)

    def _advance_orbits(self, world: World, dt: float) -> None:
        """推进所有天体轨道"""
        dt_days = dt / 86400.0  # 转换为天

        for entity, (body,) in world.get_components(CelestialBodyComponent):
            if body is None:
                continue
            TidalSystem.advance_phase(body, dt_days)

    def _update_tides(self, world: World, dt: float) -> None:
        """根据天体引力更新潮汐"""
        # 收集所有天体的潮汐力贡献
        tidal_forces = []

        for entity, (body, body_space) in world.get_components(
            CelestialBodyComponent, SpaceComponent
        ):
            if body is None or body_space is None:
                continue

            # 计算潮汐力（物理量）
            force = TidalSystem.tidal_force(body)
            tidal_forces.append((force, body.current_phase, body_space))

        if not tidal_forces:
            return

        # 更新所有潮汐点
        for entity, (tide, space) in world.get_components(TideComponent, SpaceComponent):
            if tide is None or space is None:
                continue

            # 计算该位置的总潮汐力
            total_force = 0.0

            for force, phase, body_space in tidal_forces:
                # 计算该位置相对于天体的角度
                dx = space.x - body_space.x
                dy = space.y - body_space.y
                
                # 简化的角度计算
                if dx == 0 and dy == 0:
                    local_angle = 0.0
                else:
                    local_angle = self._atan2(dy, dx)

                # 潮汐力随位置变化：
                # 高潮在 phase 和 phase+π
                # 使用 cos² 近似
                angle_diff = local_angle - phase
                # 归一化到 -π~π
                while angle_diff > 3.14159:
                    angle_diff -= 6.28318
                while angle_diff < -3.14159:
                    angle_diff += 6.28318

                # cos² 分布：最大值在 0 和 π
                cos_val = self._cos(angle_diff)
                position_factor = cos_val * cos_val

                total_force += force * position_factor

            # 将潮汐力转换为水位变化
            # 无硬编码，纯物理转换
            tide_change = total_force * self.TIDE_AMPLIFICATION * dt

            # 更新当前水位
            tide.current_level += tide_change

            # 限制在合理范围（由高潮/低潮水位决定）
            tide.current_level = max(
                tide.low_tide_level,
                min(tide.high_tide_level, tide.current_level)
            )

            # 更新潮差
            tide.tide_range = tide.high_tide_level - tide.low_tide_level

    def _atan2(self, y: float, x: float) -> float:
        """简化的 atan2 计算"""
        if x == 0:
            return 1.5708 if y > 0 else -1.5708
        
        angle = self._atan(y / x)
        if x < 0:
            angle += 3.14159 if y >= 0 else -3.14159
        elif y < 0:
            angle += 6.28318
        
        return angle

    def _atan(self, x: float) -> float:
        """简化的 atan 计算（泰勒展开）"""
        if abs(x) > 1:
            # 使用恒等式：atan(x) = π/2 - atan(1/x)
            sign = 1 if x > 0 else -1
            return sign * 1.5708 - self._atan(1.0 / x)
        
        x2 = x * x
        return x * (1 - x2 / 3 + x2 * x2 / 5 - x2 * x2 * x2 / 7)

    def _cos(self, theta: float) -> float:
        """简化的余弦计算"""
        theta = theta % 6.28318
        if theta > 3.14159:
            theta = 6.28318 - theta
            sign = -1
        else:
            sign = 1
        
        theta2 = theta * theta
        result = 1 - theta2 / 2 + theta2 * theta2 / 24
        return sign * max(-1.0, min(1.0, result))
