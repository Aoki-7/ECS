#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
洪水检测系统

职责：
    - 监测环境条件（暴雨 + 土壤饱和）
    - 识别洪水风险并触发洪水事件
"""

import random
import logging
from typing import Dict, List

from core.system import System
from core.world import World
from environment.environment_component import EnvironmentComponent

logger = logging.getLogger(__name__)


class FloodDetectionSystem(System):
    """洪水检测系统"""

    tick_interval = 20

    def __init__(self):
        super().__init__()
        self._rainfall_threshold = 50.0  # mm/h
        self._soil_moisture_threshold = 0.8

    def update(self, world: World, dt: float = 1.0) -> None:
        """检查洪水风险"""
        env = world.get_environment()
        if env is None:
            return

        rainfall = getattr(env, "rainfall", 0.0)
        soil_moisture = getattr(env, "soil_moisture", 0.0)

        if rainfall > self._rainfall_threshold and soil_moisture > self._soil_moisture_threshold:
            if random.random() < 0.005:
                self._trigger_flood(world, env)

    def _trigger_flood(self, world: World, env: EnvironmentComponent) -> None:
        """触发洪水事件"""
        disaster = {
            "type": "flood",
            "x": random.randint(0, 100),
            "y": random.randint(0, 100),
            "radius": 5.0,
            "intensity": random.uniform(0.3, 0.8),
            "tick_started": world.tick_count,
        }

        logger.warning(f"[FloodDetection] 洪水在 ({disaster['x']}, {disaster['y']}) 爆发！")

        try:
            world.event_bus.publish("disaster_flood_start", disaster)
        except Exception:
            pass