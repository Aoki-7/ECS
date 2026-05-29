#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:weather_effect_system.py
@说明:天气效果系统
@时间:2026/05/29
@版本:1.0

天气对实体的直接影响：
- 高温 → 口渴加剧、热应激、掉血
- 低温 → 精力消耗、冷应激、掉血
- 降雨 → 舒适度下降
- 强风 → 疲劳增加
'''

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.physiological.health_component import HealthComponent
from human.components.physiological.temperature_component import TemperatureComponent
from space.space_component import SpaceComponent


class WeatherEffectSystem(System):
    """
    天气效果系统
    根据环境参数直接影响人类实体的生理状态
    """

    def __init__(self):
        super().__init__()

    def update(self, world: World, dt: float):
        env = world.get_environment()
        if not isinstance(env, EnvironmentComponent):
            return

        for entity, (needs, health, space) in world.get_components(
            PhysiologyNeedsComponent, HealthComponent, SpaceComponent
        ):
            needs: PhysiologyNeedsComponent
            health: HealthComponent
            space: SpaceComponent

            temp = env.air_temperature
            humidity = env.air_humidity
            wind = env.wind_speed
            rainfall = env.rainfall

            # ---------- 高温影响 ----------
            if temp > 30.0:
                # 口渴加剧
                needs.thirst += 1.0 * (temp - 30.0) * dt
                # 疲劳增加
                needs.fatigue += 0.3 * (temp - 30.0) * dt

            if temp > 35.0:
                # 热伤害
                heat_damage = 0.1 * (temp - 35.0) * dt
                health.hp -= heat_damage
                health.hp = max(0.0, health.hp)

            # ---------- 低温影响 ----------
            if temp < 10.0:
                # 精力消耗
                needs.energy -= 0.5 * (10.0 - temp) * dt

            if temp < 0.0:
                # 冻伤伤害
                cold_damage = 0.05 * abs(temp) * dt
                health.hp -= cold_damage
                health.hp = max(0.0, health.hp)

            # ---------- 降雨影响 ----------
            if rainfall > 10.0:
                needs.comfort -= 0.5 * dt

            # ---------- 强风影响 ----------
            if wind > 10.0:
                needs.fatigue += 0.3 * dt

            # ---------- 湿度影响 ----------
            if humidity < 0.3:
                needs.thirst += 0.5 * dt
            elif humidity > 0.9:
                needs.comfort -= 0.3 * dt

            # ---------- 数值安全 ----------
            needs.hunger = max(0.0, min(needs.max_hunger, needs.hunger))
            needs.thirst = max(0.0, min(needs.max_thirst, needs.thirst))
            needs.energy = max(0.0, min(needs.max_energy, needs.energy))
            needs.fatigue = max(0.0, min(needs.max_fatigue, needs.fatigue))
            needs.comfort = max(0.0, min(needs.max_comfort, needs.comfort))
