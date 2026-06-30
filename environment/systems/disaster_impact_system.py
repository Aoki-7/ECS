#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灾害影响系统

职责：
    - 处理活跃的灾害事件
    - 计算灾害对实体/环境的影响
    - 更新灾害状态（扩散/消退）
"""

import math
import logging
from typing import Dict, List, Callable

from core.system import System
from core.world import World
from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent

logger = logging.getLogger(__name__)


class DisasterImpactSystem(System):
    """灾害影响系统"""

    tick_interval = 1

    def __init__(self):
        super().__init__()
        self._active_disasters: Dict[str, List[Dict]] = {}
        self._disaster_history: List[Dict] = []

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新活跃灾害"""
        env = world.get_environment()

        for disaster_type, disasters in list(self._active_disasters.items()):
            for disaster in list(disasters):
                if disaster_type == "fire":
                    self._update_fire(world, disaster, env, dt)
                elif disaster_type == "flood":
                    self._update_flood(world, disaster, env, dt)
                elif disaster_type == "drought":
                    self._update_drought(world, disaster, env, dt)

    def _update_fire(self, world: World, disaster: Dict, env: EnvironmentComponent, dt: float) -> None:
        """更新火灾状态"""
        spread_rate = 0.5 * disaster["intensity"]
        disaster["radius"] += spread_rate * dt

        self._affect_entities_in_radius(world, disaster, self._fire_damage)

        if env and getattr(env, "rainfall", 0.0) > 10.0:
            disaster["intensity"] -= 0.1 * dt

        if disaster["intensity"] <= 0.0:
            logger.info(f"[DisasterImpact] 火灾在 ({disaster['x']}, {disaster['y']}) 熄灭")
            self._active_disasters["fire"].remove(disaster)

    def _update_flood(self, world: World, disaster: Dict, env: EnvironmentComponent, dt: float) -> None:
        """更新洪水状态"""
        disaster["radius"] += 0.2 * dt
        self._affect_entities_in_radius(world, disaster, self._flood_damage)

        disaster["intensity"] -= 0.05 * dt
        if disaster["intensity"] <= 0.0:
            logger.info(f"[DisasterImpact] 洪水在 ({disaster['x']}, {disaster['y']}) 消退")
            self._active_disasters["flood"].remove(disaster)

    def _update_drought(self, world: World, disaster: Dict, env: EnvironmentComponent, dt: float) -> None:
        """更新干旱状态"""
        disaster["duration"] -= dt

        for entity, (soil) in world.get_components(SoilComponent):
            soil.moisture = max(
                getattr(soil, "wilting_point", 0.1),
                soil.moisture - 0.01 * dt * disaster["intensity"]
            )

        if disaster["duration"] <= 0:
            logger.info("[DisasterImpact] 干旱结束")
            self._active_disasters["drought"].remove(disaster)

    def _affect_entities_in_radius(
        self, world: World, disaster: Dict, damage_fn: Callable
    ) -> None:
        """影响范围内的实体"""
        cx, cy = disaster["x"], disaster["y"]
        radius = disaster["radius"]

        for entity, (space) in world.get_components(SpaceComponent):
            dist = math.hypot(space.x - cx, space.y - cy)
            if dist <= radius:
                damage_fn(world, entity, disaster, dist)

    def _fire_damage(self, world: World, entity, disaster: Dict, distance: float) -> None:
        """火灾伤害"""
        intensity = disaster["intensity"] * (1.0 - distance / max(1.0, disaster["radius"]))
        lifecycle = world.get_component(entity, LifeCycleComponent)
        if lifecycle:
            lifecycle.health = getattr(lifecycle, "health", 1.0) - intensity * 0.1

    def _flood_damage(self, world: World, entity, disaster: Dict, distance: float) -> None:
        """洪水伤害"""
        needs = world.get_component(entity, PhysiologyNeedsComponent)
        if needs:
            needs.energy = max(0.0, getattr(needs, "energy", 100.0) - 5.0)

    def add_disaster(self, disaster: Dict) -> None:
        """添加灾害事件"""
        disaster_type = disaster.get("type")
        if disaster_type:
            self._active_disasters.setdefault(disaster_type, []).append(disaster)
            self._disaster_history.append(disaster)

    def get_active_disasters(self) -> Dict[str, List[Dict]]:
        """获取活跃灾害"""
        return self._active_disasters.copy()

    def get_disaster_history(self) -> List[Dict]:
        """获取灾害历史"""
        return self._disaster_history.copy()
