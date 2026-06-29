#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火灾检测系统

职责：
    - 监测环境条件（高温 + 低湿度 + 有风）
    - 识别火灾风险并触发火灾事件
"""

import random
import logging
from typing import Dict, List, Optional

from core.system import System
from core.world import World
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent
from plant.components.plant_component import PlantComponent

logger = logging.getLogger(__name__)


class FireDetectionSystem(System):
    """火灾检测系统"""

    tick_interval = 20

    def __init__(self):
        super().__init__()
        self._fire_risk_threshold = 0.6

    def update(self, world: World, dt: float = 1.0) -> None:
        """检查火灾风险"""
        env = world.get_environment()
        if env is None:
            return

        temp = getattr(env, "air_temperature", 20.0)
        humidity = getattr(env, "air_humidity", 0.5) * 100.0
        wind = getattr(env, "wind_speed", 0.0)

        fire_risk = self._calculate_fire_risk(temp, humidity, wind)

        if fire_risk > self._fire_risk_threshold and random.random() < fire_risk * 0.01:
            self._trigger_fire(world, env)

    def _calculate_fire_risk(self, temp: float, humidity: float, wind: float) -> float:
        """计算火灾风险指数"""
        risk = 0.0
        if temp > 35.0:
            risk += (temp - 35.0) / 15.0 * 0.4
        if humidity < 30.0:
            risk += (30.0 - humidity) / 30.0 * 0.4
        if wind > 5.0:
            risk += min(0.2, wind / 50.0)
        return min(1.0, risk)

    def _trigger_fire(self, world: World, env: EnvironmentComponent) -> None:
        """触发火灾事件"""
        plant_positions = []
        for entity, (space, plant) in world.get_components(SpaceComponent, PlantComponent):
            plant_positions.append((space.x, space.y))

        if not plant_positions:
            return

        start_x, start_y = random.choice(plant_positions)

        logger.warning(f"[FireDetection] 火灾在 ({start_x}, {start_y}) 爆发！")

        try:
            world.event_bus.publish("disaster_fire_start", {
                "x": start_x, "y": start_y,
                "tick": world.tick_count,
            })
        except Exception:
            pass
