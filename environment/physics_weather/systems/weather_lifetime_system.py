#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
物理异常生命周期管理（精简版）

旧系统：管理事件阶段切换（FORMING/MATURE/DECAYING/DISSIPATED）
新系统：只清理持续时间过长或实体已失效的异常记录

异常的存在/结束完全由物理量是否回归常态决定，
不需要人工定义生命周期阶段。
"""

from core.system import System
from core.world import World

from environment.physics_weather.components.weather_event_components import (
    PhysicalAnomalyComponent,
)


class WeatherLifetimeSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    异常生命周期系统

    仅做两件事：
    1. 清理持续时间超过上限的异常（防止无限累积）
    2. 清理实体已失效的异常引用
    """

    # 异常最大持续时间（小时），超过自动清理
    MAX_ANOMALY_DURATION_HOURS: float = 720.0  # 30天

    def update(self, world: World, delta_hours: float):
        expired = []

        for entity, (anomaly,) in world.get_components(PhysicalAnomalyComponent):
            anomaly: PhysicalAnomalyComponent

            # 持续时间检查
            if anomaly.duration_hours > self.MAX_ANOMALY_DURATION_HOURS:
                expired.append(entity)
                continue

            # 实体有效性检查（已由异常检测系统处理大部分）
            if not world.has_entity(entity):
                expired.append(entity)

        for entity in expired:
            if world.has_entity(entity):
                world.remove_entity(entity)
