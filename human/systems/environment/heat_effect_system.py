#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
HeatEffectSystem - 高温效果系统

高温 >30°C：口渴加剧、疲劳增加
高温 >35°C：热伤害（hp 下降）
"""

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.physiological.health_component import HealthComponent
from space.space_component import SpaceComponent


class HeatEffectSystem(System):
    """高温对实体的影响"""

    priority = 25

    # 魔法值常量
    TEMP_THRESHOLD_MILD = 30.0   # 轻度高温阈值
    TEMP_THRESHOLD_SEVERE = 35.0  # 严重高温阈值
    THIRST_RATE = 1.0            # 口渴增长系数
    FATIGUE_RATE = 0.3           # 疲劳增长系数
    HEAT_DAMAGE_RATE = 0.1       # 热伤害系数

    def update(self, world: World, dt: float):
        super().update(world, dt)
        env = world.get_environment()
        if not isinstance(env, EnvironmentComponent):
            return

        temp = env.air_temperature
        if temp <= self.TEMP_THRESHOLD_MILD:
            return

        for entity, (needs, health, space) in world.get_components(
            PhysiologyNeedsComponent, HealthComponent, SpaceComponent
        ):
            # 轻度高温
            if temp > self.TEMP_THRESHOLD_MILD:
                needs.thirst += self.THIRST_RATE * (temp - self.TEMP_THRESHOLD_MILD) * dt
                needs.fatigue += self.FATIGUE_RATE * (temp - self.TEMP_THRESHOLD_MILD) * dt

            # 严重高温
            if temp > self.TEMP_THRESHOLD_SEVERE:
                heat_damage = self.HEAT_DAMAGE_RATE * (temp - self.TEMP_THRESHOLD_SEVERE) * dt
                health.hp = max(0.0, min(health.max_hp, health.hp - heat_damage))

            # Clamp
            needs.thirst = max(0.0, min(needs.max_thirst, needs.thirst))
            needs.fatigue = max(0.0, min(needs.max_fatigue, needs.fatigue))
