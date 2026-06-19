#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:energy_system.py
@说明:精力系统（拆分自 PhysiologyNeedsSystem）
@时间:2026/05/29
@版本:1.0
'''

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType


class EnergySystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    精力系统
    负责精力自然衰减及生理反馈（饥饿/口渴/疲劳）
    """

    BASE_ENERGY_DECAY = 1.5   # 基础精力衰减 /小时

    def update(self, world: World, dt: float):
        env = world.get_environment()
        env_is_valid = isinstance(env, EnvironmentComponent)

        for entity, (needs,) in world.get_components(PhysiologyNeedsComponent):
            needs: PhysiologyNeedsComponent

            # 检测睡眠状态
            action = world.get_component(entity, ActionComponent)
            is_sleeping = (
                action is not None
                and action.current_action == ActionType.SLEEP
            )
            metabolic_mult = 0.2 if is_sleeping else 1.0

            # 归一化
            h = needs.hunger / needs.max_hunger
            t = needs.thirst / needs.max_thirst
            e = needs.energy / needs.max_energy

            # 耦合项
            hunger_to_energy = 1.0 * h
            thirst_to_energy = 2.0 * t
            energy_feedback = 1.0 - e

            # 精力衰减
            energy_decay = (
                self.BASE_ENERGY_DECAY
                + hunger_to_energy
                + thirst_to_energy
            ) * metabolic_mult * dt
            needs.energy -= energy_decay

            # 环境耦合：极端温度消耗能量
            if env_is_valid:
                if env.air_temperature > 30.0:
                    needs.energy -= 0.15 * (env.air_temperature - 30.0) * dt
                elif env.air_temperature < 10.0:
                    needs.energy -= 0.08 * (10.0 - env.air_temperature) * dt

            # 极端饥饿/口渴惩罚（额外精力消耗）
            if needs.thirst > 80.0:
                needs.energy -= 3.0 * dt
            if needs.hunger > 80.0:
                needs.energy -= 1.5 * dt

            # Clamp
            needs.energy = max(0.0, min(needs.max_energy, needs.energy))
