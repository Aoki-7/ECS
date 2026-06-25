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
from core.constants import (
    DEFAULT_TEMPERATURE,
    DEFAULT_HUMIDITY,
    DEFAULT_RAINFALL,
)

from environment.environment_component import EnvironmentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.health_status_component import HealthStatusComponent
from space.space_component import SpaceComponent


class WeatherEffectSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    天气效果系统
    根据环境参数直接影响人类实体的生理状态
    """

    # 高温阈值
    TEMP_HIGH_MILD = 30.0
    TEMP_HIGH_SEVERE = 35.0
    # 低温阈值
    TEMP_LOW_MILD = 10.0
    TEMP_LOW_SEVERE = 0.0
    # 降雨阈值
    RAIN_THRESHOLD = 10.0
    # 强风阈值
    WIND_THRESHOLD = 10.0
    # 低湿度阈值
    HUMIDITY_LOW = 0.3
    # 高湿度阈值
    HUMIDITY_HIGH = 0.9

    # 效果系数
    THIRST_RATE_HIGH_TEMP = 1.0
    FATIGUE_RATE_HIGH_TEMP = 0.3
    HEAT_DAMAGE_RATE = 0.1
    ENERGY_DRAIN_LOW_TEMP = 0.5
    COLD_DAMAGE_RATE = 0.05
    COMFORT_PENALTY_RAIN = 0.5
    FATIGUE_RATE_WIND = 0.3
    THIRST_RATE_LOW_HUMIDITY = 0.5
    COMFORT_PENALTY_HIGH_HUMIDITY = 0.3

    def __init__(self):
        super().__init__()

    def update(self, world: World, dt: float):
        env = world.get_environment()
        if not isinstance(env, EnvironmentComponent):
            return

        # 缓存环境参数到局部变量，避免循环内重复属性访问
        temp = env.air_temperature
        humidity = env.air_humidity
        wind = env.wind_speed
        rainfall = env.rainfall

        for entity, (needs, health, space) in world.get_components(
            PhysiologyNeedsComponent, HealthStatusComponent, SpaceComponent
        ):
            needs: PhysiologyNeedsComponent
            health: HealthStatusComponent
            space: SpaceComponent

            # ---------- 高温影响 ----------
            if temp > self.TEMP_HIGH_MILD:
                # 口渴加剧
                needs.thirst += self.THIRST_RATE_HIGH_TEMP * (temp - self.TEMP_HIGH_MILD) * dt
                # 疲劳增加
                needs.fatigue += self.FATIGUE_RATE_HIGH_TEMP * (temp - self.TEMP_HIGH_MILD) * dt

            if temp > self.TEMP_HIGH_SEVERE:
                # 热伤害
                heat_damage = self.HEAT_DAMAGE_RATE * (temp - self.TEMP_HIGH_SEVERE) * dt
                health.hp = max(0.0, min(health.max_hp, health.hp - heat_damage))

            # ---------- 低温影响 ----------
            if temp < self.TEMP_LOW_MILD:
                # 精力消耗
                needs.energy -= self.ENERGY_DRAIN_LOW_TEMP * (self.TEMP_LOW_MILD - temp) * dt

            if temp < self.TEMP_LOW_SEVERE:
                # 冻伤伤害
                cold_damage = self.COLD_DAMAGE_RATE * abs(temp) * dt
                health.hp = max(0.0, min(health.max_hp, health.hp - cold_damage))

            # ---------- 降雨影响 ----------
            if rainfall > self.RAIN_THRESHOLD:
                needs.comfort -= self.COMFORT_PENALTY_RAIN * dt

            # ---------- 强风影响 ----------
            if wind > self.WIND_THRESHOLD:
                needs.fatigue += self.FATIGUE_RATE_WIND * dt

            # ---------- 湿度影响 ----------
            if humidity < self.HUMIDITY_LOW:
                needs.thirst += self.THIRST_RATE_LOW_HUMIDITY * dt
            elif humidity > self.HUMIDITY_HIGH:
                needs.comfort -= self.COMFORT_PENALTY_HIGH_HUMIDITY * dt

            # ---------- 数值安全 ----------
            needs.hunger = max(0.0, min(needs.max_hunger, needs.hunger))
            needs.thirst = max(0.0, min(needs.max_thirst, needs.thirst))
            needs.energy = max(0.0, min(needs.max_energy, needs.energy))
            needs.fatigue = max(0.0, min(needs.max_fatigue, needs.fatigue))
            needs.comfort = max(0.0, min(needs.max_comfort, needs.comfort))