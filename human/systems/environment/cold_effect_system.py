#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
ColdEffectSystem - 低温效果系统

低温 <10°C：精力消耗
低温 <0°C：冻伤伤害（hp 下降）
"""

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.health_component import HealthComponent
from space.space_component import SpaceComponent


class ColdEffectSystem(System):
    """低温对实体的影响"""

    priority = 25

    # 魔法值常量
    TEMP_THRESHOLD_MILD = 10.0   # 轻度低温阈值
    TEMP_THRESHOLD_SEVERE = 0.0   # 严重低温阈值
    ENERGY_DRAIN_RATE = 0.5      # 精力消耗系数
    COLD_DAMAGE_RATE = 0.05      # 冻伤伤害系数

    def update(self, world: World, dt: float):
        super().update(world, dt)
        env = world.get_environment()
        if not isinstance(env, EnvironmentComponent):
            return

        temp = env.air_temperature
        if temp >= self.TEMP_THRESHOLD_MILD:
            return

        for entity, (needs, health, space) in world.get_components(
            PhysiologyNeedsComponent, HealthComponent, SpaceComponent
        ):
            # 轻度低温
            if temp < self.TEMP_THRESHOLD_MILD:
                needs.energy -= self.ENERGY_DRAIN_RATE * (self.TEMP_THRESHOLD_MILD - temp) * dt

            # 严重低温
            if temp < self.TEMP_THRESHOLD_SEVERE:
                cold_damage = self.COLD_DAMAGE_RATE * abs(temp) * dt
                health.hp = max(0.0, min(health.max_hp, health.hp - cold_damage))

            # Clamp
            needs.energy = max(0.0, min(needs.max_energy, needs.energy))
