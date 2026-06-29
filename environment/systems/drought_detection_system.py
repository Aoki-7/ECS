#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
干旱检测系统

职责：
    - 监测环境条件（长期无雨 + 高温）
    - 识别干旱风险并触发干旱事件
"""

import random
import logging
from typing import Dict, List

from core.system import System
from core.world import World
from environment.environment_component import EnvironmentComponent

logger = logging.getLogger(__name__)


class DroughtDetectionSystem(System):
    """干旱检测系统"""

    tick_interval = 20

    def __init__(self):
        super().__init__()
        self._rainfall_threshold = 1.0  # mm
        self._temp_threshold = 30.0     # °C

    def update(self, world: World, dt: float = 1.0) -> None:
        """检查干旱风险"""
        env = world.get_environment()
        if env is None:
            return

        rainfall = getattr(env, "rainfall", 0.0)
        temp = getattr(env, "air_temperature", 20.0)

        if rainfall < self._rainfall_threshold and temp > self._temp_threshold:
            if random.random() < 0.002:
                self._trigger_drought(world, env)

    def _trigger_drought(self, world: World, env: EnvironmentComponent) -> None:
        """触发干旱事件"""
        disaster = {
            "type": "drought",
            "x": 50,
            "y": 50,
            "radius": 100.0,
            "intensity": random.uniform(0.3, 0.9),
            "tick_started": world.tick_count,
            "duration": random.randint(50, 200),
        }

        logger.warning(f"[DroughtDetection] 干旱开始！预计持续 {disaster['duration']} ticks")

        try:
            world.event_bus.publish("disaster_drought_start", disaster)
        except Exception:
            pass
