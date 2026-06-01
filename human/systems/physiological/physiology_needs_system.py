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
from core.components.action_component import ActionComponent, ActionType


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
    BASE_HUNGER_RATE = 4.0

    # ── 口渴参数 ──
    BASE_THIRST_RATE = 3.5

    # ── 精力参数 ──
    BASE_ENERGY_DECAY = 1.5

    # ── 社交参数 ──
    SOCIAL_DECAY_RATE = 0.3

    def update(self, world: World, dt: float):
        env = world.get_environment()
        env_is_valid = isinstance(env, EnvironmentComponent)

        # 缓存环境属性到局部变量
        env_temp = env.air_temperature if env_is_valid else 20.0
        env_humidity = env.air_humidity if env_is_valid else 0.5
        env_wind = env.wind_speed if env_is_valid else 0.0
        env_rainfall = env.rainfall if env_is_valid else 0.0
        env_water_stress = env.water_stress_index if env_is_valid else 0.0

        for entity, (needs,) in world.get_components(PhysiologyNeedsComponent):
            needs: PhysiologyNeedsComponent

            # 检测睡眠状态（一次查询，复用给多个子逻辑）
            action = world.get_component(entity, ActionComponent)
            is_sleeping = (
                action is not None
                and action.current_action == ActionType.SLEEP
            )
            metabolic_mult = 0.2 if is_sleeping else 1.0

            # ═══════════════════════════════════════════════
            # 1. 饥饿更新
            # ═══════════════════════════════════════════════
            hunger_rate = self.BASE_HUNGER_RATE * metabolic_mult * dt
            needs.hunger = min(needs.max_hunger, needs.hunger + hunger_rate)

            # ═══════════════════════════════════════════════
            # 2. 口渴更新
            # ═══════════════════════════════════════════════
            h = needs.hunger / needs.max_hunger
            hunger_to_thirst = 0.5 * h
            thirst_rate = (
                self.BASE_THIRST_RATE + hunger_to_thirst
            ) * metabolic_mult * dt
            needs.thirst += thirst_rate

            if env_is_valid:
                needs.thirst += 1.0 * env_water_stress * dt
                if env_humidity < 0.3:
                    needs.thirst += 0.5 * dt

            needs.thirst = max(0.0, min(needs.max_thirst, needs.thirst))

            # ═══════════════════════════════════════════════
            # 3. 精力更新
            # ═══════════════════════════════════════════════
            h_norm = needs.hunger / needs.max_hunger
            t_norm = needs.thirst / needs.max_thirst
            e_norm = needs.energy / needs.max_energy

            hunger_to_energy = 1.0 * h_norm
            thirst_to_energy = 2.0 * t_norm
            energy_feedback = 1.0 - e_norm

            energy_decay = (
                self.BASE_ENERGY_DECAY
                + hunger_to_energy
                + thirst_to_energy
            ) * metabolic_mult * dt
            needs.energy -= energy_decay

            if env_is_valid:
                if env_temp > 30.0:
                    needs.energy -= 0.15 * (env_temp - 30.0) * dt
                elif env_temp < 10.0:
                    needs.energy -= 0.08 * (10.0 - env_temp) * dt

            if needs.thirst > 80.0:
                needs.energy -= 3.0 * dt
            if needs.hunger > 80.0:
                needs.energy -= 1.5 * dt

            needs.energy = max(0.0, min(needs.max_energy, needs.energy))

            # ═══════════════════════════════════════════════
            # 4. 舒适度/疲劳更新
            # ═══════════════════════════════════════════════
            if env_is_valid:
                if env_temp > 25.0:
                    needs.fatigue += 0.5 * (env_temp - 25.0) * dt
                if env_humidity > 0.9:
                    needs.comfort -= 0.3 * dt

            needs.fatigue = max(0.0, min(needs.max_fatigue, needs.fatigue))
            needs.comfort = max(0.0, min(needs.max_comfort, needs.comfort))

            # ═══════════════════════════════════════════════
            # 5. 社交需求衰减
            # ═══════════════════════════════════════════════
            needs.social -= self.SOCIAL_DECAY_RATE * dt
            needs.social = max(0.0, min(needs.max_social, needs.social))

            # ═══════════════════════════════════════════════
            # 6. 全局数值安全
            # ═══════════════════════════════════════════════
            needs.hunger = max(0.0, min(needs.max_hunger, needs.hunger))


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
