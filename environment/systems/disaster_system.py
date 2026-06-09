#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境灾害系统

v3.0.1 新增 — P1

核心设计原则：
- 灾害从环境条件自然涌现，非随机事件
- 火灾：高温 + 干旱 + 风 → 火势蔓延
- 洪水：暴雨 + 地形低洼 → 积水扩散
- 干旱：长期无雨 + 高温 → 土壤干裂
- 灾害影响生态系统，生物可适应/逃避
"""

import random
import math
from typing import Dict, List, Optional, Set, Tuple

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

import logging

logger = logging.getLogger(__name__)


class DisasterSystem(System):
    """
    环境灾害系统

    职责：
        - 监测环境条件，识别灾害风险
        - 执行灾害影响（火灾蔓延、洪水扩散、干旱加剧）
        - 记录灾害历史
    """

    tick_interval = 10  # 每10帧检查一次

    def __init__(self):
        super().__init__()
        self._active_disasters: Dict[str, List[Dict]] = {}  # type -> list of active disasters
        self._disaster_history: List[Dict] = []

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新灾害状态"""
        env = world.get_environment()
        if env is None:
            return

        # 检查新灾害触发
        self._check_fire_risk(world, env)
        self._check_flood_risk(world, env)
        self._check_drought_risk(world, env)

        # 更新活跃灾害
        self._update_active_disasters(world, dt)

    def _check_fire_risk(self, world: World, env: EnvironmentComponent) -> None:
        """检查火灾风险"""
        # 火灾条件：高温 (>35°C) + 低湿度 (<30%) + 有风
        temp = getattr(env, "air_temperature", 20.0)
        humidity = getattr(env, "air_humidity", 0.5) * 100.0
        wind = getattr(env, "wind_speed", 0.0)

        fire_risk = 0.0
        if temp > 35.0:
            fire_risk += (temp - 35.0) / 15.0 * 0.4
        if humidity < 30.0:
            fire_risk += (30.0 - humidity) / 30.0 * 0.4
        if wind > 5.0:
            fire_risk += min(0.2, wind / 50.0)

        fire_risk = min(1.0, fire_risk)

        # 随机触发
        if fire_risk > 0.6 and random.random() < fire_risk * 0.01:
            self._start_fire(world, env)

    def _start_fire(self, world: World, env: EnvironmentComponent) -> None:
        """开始火灾"""
        # 随机选择起始位置
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        # 找到有植物的位置
        from plant.components.plant_component import PlantComponent
        plant_positions = []
        for entity, (space, plant) in world.get_components(SpaceComponent, PlantComponent):
            plant_positions.append((space.x, space.y))

        if not plant_positions:
            return

        start_x, start_y = random.choice(plant_positions)

        disaster = {
            "type": "fire",
            "x": start_x,
            "y": start_y,
            "radius": 1.0,
            "intensity": random.uniform(0.5, 1.0),
            "tick_started": world.tick_count,
        }

        self._active_disasters.setdefault("fire", []).append(disaster)
        self._disaster_history.append(disaster)

        logger.warning(f"[Disaster] 火灾在 ({start_x}, {start_y}) 爆发！")

        # 发布事件
        try:
            from core.event_bus import EventBus
            EventBus.get_instance().publish("disaster_fire", {
                "x": start_x, "y": start_y, "intensity": disaster["intensity"],
            })
        except Exception:
            pass

    def _check_flood_risk(self, world: World, env: EnvironmentComponent) -> None:
        """检查洪水风险"""
        # 洪水条件：暴雨 (>50mm/h) + 持续降雨
        rainfall = getattr(env, "rainfall", 0.0)
        soil_moisture = getattr(env, "soil_moisture", 0.0)

        if rainfall > 50.0 and soil_moisture > 0.8:
            if random.random() < 0.005:
                self._start_flood(world, env)

    def _start_flood(self, world: World, env: EnvironmentComponent) -> None:
        """开始洪水"""
        # 洪水从低洼处开始
        disaster = {
            "type": "flood",
            "x": random.randint(0, 100),
            "y": random.randint(0, 100),
            "radius": 5.0,
            "intensity": random.uniform(0.3, 0.8),
            "tick_started": world.tick_count,
        }

        self._active_disasters.setdefault("flood", []).append(disaster)
        self._disaster_history.append(disaster)

        logger.warning(f"[Disaster] 洪水在 ({disaster['x']}, {disaster['y']}) 爆发！")

    def _check_drought_risk(self, world: World, env: EnvironmentComponent) -> None:
        """检查干旱风险"""
        # 干旱：长期无雨 + 高温
        rainfall = getattr(env, "rainfall", 0.0)
        temp = getattr(env, "air_temperature", 20.0)

        if rainfall < 1.0 and temp > 30.0:
            # 检查是否已有活跃干旱
            active_droughts = self._active_disasters.get("drought", [])
            if not active_droughts:
                if random.random() < 0.002:
                    self._start_drought(world, env)

    def _start_drought(self, world: World, env: EnvironmentComponent) -> None:
        """开始干旱"""
        disaster = {
            "type": "drought",
            "x": 50,  # 全局影响
            "y": 50,
            "radius": 100.0,
            "intensity": random.uniform(0.3, 0.9),
            "tick_started": world.tick_count,
            "duration": random.randint(50, 200),
        }

        self._active_disasters.setdefault("drought", []).append(disaster)
        self._disaster_history.append(disaster)

        logger.warning(f"[Disaster] 干旱开始！预计持续 {disaster['duration']} ticks")

    def _update_active_disasters(self, world: World, dt: float) -> None:
        """更新活跃灾害"""
        for disaster_type, disasters in list(self._active_disasters.items()):
            for disaster in disasters[:]:
                if disaster_type == "fire":
                    self._update_fire(world, disaster, dt)
                elif disaster_type == "flood":
                    self._update_flood(world, disaster, dt)
                elif disaster_type == "drought":
                    self._update_drought(world, disaster, dt)

    def _update_fire(self, world: World, disaster: Dict, dt: float) -> None:
        """更新火灾（蔓延）"""
        # 火势蔓延
        env = world.get_environment()
        wind = getattr(env, "wind_speed", 0.0) if env else 0.0

        spread_rate = 0.1 + wind * 0.02
        disaster["radius"] += spread_rate * dt

        # 影响范围内的实体
        self._affect_entities_in_radius(world, disaster, self._fire_damage)

        # 火势衰减（降雨或燃料耗尽）
        if env and getattr(env, "rainfall", 0.0) > 10.0:
            disaster["intensity"] -= 0.1 * dt

        if disaster["intensity"] <= 0.0:
            logger.info(f"[Disaster] 火灾在 ({disaster['x']}, {disaster['y']}) 熄灭")
            self._active_disasters["fire"].remove(disaster)

    def _update_flood(self, world: World, disaster: Dict, dt: float) -> None:
        """更新洪水（扩散/消退）"""
        # 洪水扩散
        disaster["radius"] += 0.2 * dt

        # 影响实体
        self._affect_entities_in_radius(world, disaster, self._flood_damage)

        # 洪水消退（蒸发/渗透）
        disaster["intensity"] -= 0.05 * dt

        if disaster["intensity"] <= 0.0:
            logger.info(f"[Disaster] 洪水在 ({disaster['x']}, {disaster['y']}) 消退")
            self._active_disasters["flood"].remove(disaster)

    def _update_drought(self, world: World, disaster: Dict, dt: float) -> None:
        """更新干旱"""
        disaster["duration"] -= dt

        # 全局影响：降低土壤湿度
        for entity, soil in world.get_components(SoilComponent):
            soil.moisture = max(soil.wilting_point, soil.moisture - 0.01 * dt * disaster["intensity"])

        if disaster["duration"] <= 0:
            logger.info("[Disaster] 干旱结束")
            self._active_disasters["drought"].remove(disaster)

    def _affect_entities_in_radius(
        self, world: World, disaster: Dict, damage_fn
    ) -> None:
        """影响范围内的实体"""
        cx, cy = disaster["x"], disaster["y"]
        radius = disaster["radius"]

        for entity, space in world.get_components(SpaceComponent):
            dist = math.hypot(space.x - cx, space.y - cy)
            if dist <= radius:
                damage_fn(world, entity, disaster, dist)

    def _fire_damage(self, world, entity, disaster, distance) -> None:
        """火灾伤害"""
        from biology.lifecycle.components.life_cycle_component import LifeCycleComponent

        intensity = disaster["intensity"] * (1.0 - distance / max(1.0, disaster["radius"]))

        # 对植物造成伤害
        lifecycle = world.get_component(entity, LifeCycleComponent)
        if lifecycle:
            lifecycle.health = getattr(lifecycle, "health", 1.0) - intensity * 0.1

    def _flood_damage(self, world, entity, disaster, distance) -> None:
        """洪水伤害"""
        from biology.components.physiology_needs_component import PhysiologyNeedsComponent

        needs = world.get_component(entity, PhysiologyNeedsComponent)
        if needs:
            needs.energy = max(0.0, getattr(needs, "energy", 100.0) - 5.0)

    def get_active_disasters(self) -> Dict[str, List[Dict]]:
        """获取活跃灾害"""
        return self._active_disasters.copy()

    def get_disaster_history(self, limit: int = 100) -> List[Dict]:
        """获取灾害历史"""
        return self._disaster_history[-limit:]
