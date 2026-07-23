#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:physiology_needs_system.py
@说明:生理需求系统（合并版）
@时间:2026/05/30
@版本:1.0

合并原 HungerSystem / ThirstSystem / EnergySystem / ComfortSystem / SocialNeedSystem
将 5 次 get_components(PhysiologyNeedsComponent) 遍历合并为 1 次。
'''

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType


class PhysiologyNeedsSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    生理需求合并系统
    
    单次遍历更新所有生理指标：
    - 饥饿值自然增长
    - 口渴值自然增长 + 环境耦合
    - 精力自然衰减 + 生理反馈 + 环境耦合
    - 舒适度/疲劳的环境耦合
    - 社交需求自然衰减
    """

    priority = 40

    # ── 饥饿参数 ──
    # 与原 HungerSystem（tick_interval=20, BASE=4.0）等效：0.2/tick
    BASE_HUNGER_RATE = 0.2

    # ── 口渴参数 ──
    # 与原 ThirstSystem（tick_interval=20, BASE=3.5）等效：0.175/tick
    BASE_THIRST_RATE = 0.175

    # ── 精力参数 ──
    # 与原 EnergySystem（tick_interval=20, BASE=1.5）等效：0.075/tick
    BASE_ENERGY_DECAY = 0.075

    # ── 社交参数 ──
    # 与原 SocialNeedSystem（tick_interval=20, BASE=0.3）等效：0.015/tick
    SOCIAL_DECAY_RATE = 0.015

    def update(self, world: World, dt: float):
        env = world.get_environment()
        env_is_valid = isinstance(env, EnvironmentComponent)

        env_cache = self._cache_env(env, env_is_valid)

        for entity, (needs,) in world.get_components(PhysiologyNeedsComponent):
            needs: PhysiologyNeedsComponent
            action = world.get_component(entity, ActionComponent)
            is_sleeping = action is not None and action.current_action == ActionType.SLEEP
            metabolic_mult = 0.2 if is_sleeping else 1.0

            self._update_hunger(needs, metabolic_mult, dt)
            self._update_thirst(needs, env_cache, env_is_valid, metabolic_mult, dt)
            self._update_energy(needs, env_cache, env_is_valid, metabolic_mult, dt)
            self._update_comfort_fatigue(needs, env_cache, env_is_valid, dt)
            self._update_social(needs, dt)

    def _cache_env(self, env, env_is_valid: bool) -> dict:
        """缓存环境属性到字典，避免循环内重复属性访问"""
        return {
            "temp": env.air_temperature if env_is_valid else 20.0,
            "humidity": env.air_humidity if env_is_valid else 0.5,
            "wind": env.wind_speed if env_is_valid else 0.0,
            "rainfall": env.rainfall if env_is_valid else 0.0,
            "water_stress": env.water_stress_index if env_is_valid else 0.0,
        }

    def _update_hunger(self, needs: PhysiologyNeedsComponent, metabolic_mult: float, dt: float):
        """饥饿值自然增长"""
        hunger_rate = self.BASE_HUNGER_RATE * metabolic_mult * dt
        needs.hunger = min(needs.max_hunger, needs.hunger + hunger_rate)

    def _update_thirst(self, needs: PhysiologyNeedsComponent, env_cache: dict, env_is_valid: bool, metabolic_mult: float, dt: float):
        """口渴值自然增长 + 环境耦合"""
        h = needs.hunger / needs.max_hunger
        thirst_rate = (self.BASE_THIRST_RATE + 0.5 * h) * metabolic_mult * dt
        needs.thirst += thirst_rate

        if env_is_valid:
            needs.thirst += 1.0 * env_cache["water_stress"] * dt
            if env_cache["humidity"] < 0.3:
                needs.thirst += 0.5 * dt

        needs.thirst = max(0.0, min(needs.max_thirst, needs.thirst))

    def _update_energy(self, needs: PhysiologyNeedsComponent, env_cache: dict, env_is_valid: bool, metabolic_mult: float, dt: float):
        """精力自然衰减 + 生理反馈 + 环境耦合"""
        h_norm = needs.hunger / needs.max_hunger
        t_norm = needs.thirst / needs.max_thirst
        e_norm = needs.energy / needs.max_energy

        energy_decay = (self.BASE_ENERGY_DECAY + 1.0 * h_norm + 2.0 * t_norm) * metabolic_mult * dt
        needs.energy -= energy_decay

        if env_is_valid:
            env_temp = env_cache["temp"]
            if env_temp > 30.0:
                needs.energy -= 0.15 * (env_temp - 30.0) * dt
            elif env_temp < 10.0:
                needs.energy -= 0.08 * (10.0 - env_temp) * dt

        if needs.thirst > 80.0:
            needs.energy -= 2.0 * dt
        if needs.hunger > 80.0:
            needs.energy -= 1.0 * dt

        needs.energy = max(0.0, min(needs.max_energy, needs.energy))

    def _update_comfort_fatigue(self, needs: PhysiologyNeedsComponent, env_cache: dict, env_is_valid: bool, dt: float):
        """舒适度/疲劳的环境耦合"""
        if env_is_valid:
            if env_cache["temp"] > 25.0:
                needs.fatigue += 0.5 * (env_cache["temp"] - 25.0) * dt
            if env_cache["humidity"] > 0.9:
                needs.comfort -= 0.3 * dt

        needs.fatigue = max(0.0, min(needs.max_fatigue, needs.fatigue))
        needs.comfort = max(0.0, min(needs.max_comfort, needs.comfort))

    def _update_social(self, needs: PhysiologyNeedsComponent, dt: float):
        """社交需求自然衰减"""
        needs.social -= self.SOCIAL_DECAY_RATE * dt
        needs.social = max(0.0, min(needs.max_social, needs.social))


class PhysiologyNeedsHelper:
    """
    生理需求辅助类

    提供安全的数值修改方法，供 SleepSystem、SocializeSystem 等调用。
    """

    @staticmethod
    def add_energy(needs: PhysiologyNeedsComponent, delta: float) -> None:
        """修改精力值（带边界）"""
        needs.energy = max(0.0, min(needs.max_energy, needs.energy + delta))

    @staticmethod
    def add_fatigue(needs: PhysiologyNeedsComponent, delta: float) -> None:
        """修改疲劳值（带边界）"""
        needs.fatigue = max(0.0, min(needs.max_fatigue, needs.fatigue + delta))

    @staticmethod
    def add_thirst(needs: PhysiologyNeedsComponent, delta: float) -> None:
        """修改口渴值（带边界）"""
        needs.thirst = max(0.0, min(needs.max_thirst, needs.thirst + delta))

    @staticmethod
    def add_hunger(needs: PhysiologyNeedsComponent, delta: float) -> None:
        """修改饥饿值（带边界）"""
        needs.hunger = max(0.0, min(needs.max_hunger, needs.hunger + delta))

    @staticmethod
    def add_social(needs: PhysiologyNeedsComponent, delta: float) -> None:
        """修改社交需求值（带边界）"""
        needs.social = max(0.0, min(needs.max_social, needs.social + delta))