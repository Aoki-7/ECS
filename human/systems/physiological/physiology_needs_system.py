#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:needs_system.py
@说明:生理需求系统 - 校准版
@时间:2026/03/13 13:43:48
@作者:Sherry
@版本:2.0

设计目标：在一个日循环（24小时）内，人类的生理需求会自然增长到需要行动的程度。
- 9小时不进食 → hunger > 70 → 触发EAT
- 6小时不饮水 → thirst > 70 → 触发DRINK  
- 18小时不休息 → energy < 30 → 触发SLEEP
'''

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType

class PhysiologyNeedsSystem(System):
    """
        需求系统
        随着时间推移，生理需求会自然增长，并且相互影响。
    """
    def update(self, world: World, dt: float):
        for entity, [needs] in world.get_components(PhysiologyNeedsComponent):
            needs: PhysiologyNeedsComponent

            # --- 检测睡眠状态（睡眠时代谢率降低） ---
            action = world.get_component(entity, ActionComponent)
            is_sleeping = (action is not None and action.current_action == ActionType.SLEEP)
            metabolic_mult = 0.2 if is_sleeping else 1.0  # 睡眠时代谢降至20%

            # --- 归一化（假设范围0~100） ---
            h = needs.hunger / 100.0
            t = needs.thirst / 100.0
            e = needs.energy / 100.0

            # --- 基础变化率（校准值） ---
            # 9小时空腹→hunger=72, 6小时不喝→thirst=72
            base_hunger = 8.0
            base_thirst = 12.0
            base_energy_decay = 4.0

            # --- 耦合项 ---
            # 饥饿 → 额外消耗体力
            hunger_to_energy = 1.0 * h
            # 口渴 → 大幅消耗体力
            thirst_to_energy = 2.0 * t
            # 饥饿 → 增加口渴
            hunger_to_thirst = 0.5 * h
            # 体力低 → 抑制需求增长（保存能量）
            energy_feedback = (1.0 - e)

            # --- 更新 ---
            needs.hunger += (
                base_hunger * (1 - 0.3 * energy_feedback)
            ) * dt * metabolic_mult

            needs.thirst += (
                base_thirst + hunger_to_thirst
            ) * (1 - 0.2 * energy_feedback) * dt * metabolic_mult

            needs.energy -= (
                base_energy_decay
                + hunger_to_energy
                + thirst_to_energy
            ) * dt * metabolic_mult

            # --- 环境耦合 ---
            env = world.get_environment()
            if isinstance(env, EnvironmentComponent):
                # 干热环境加剧口渴
                needs.thirst += 2.0 * env.water_stress_index * dt
                needs.fatigue += 0.5 * max(0.0, env.air_temperature - 25.0) * dt

                # 极端温度消耗能量
                if env.air_temperature > 30:
                    needs.energy -= 1.0 * (env.air_temperature - 30) * dt
                elif env.air_temperature < 10:
                    needs.energy -= 0.5 * (10 - env.air_temperature) * dt

                # 湿度影响
                if env.air_humidity < 0.3:
                    needs.thirst += 1.5 * dt
                elif env.air_humidity > 0.9:
                    needs.add_comfort(-0.3 * dt)

            # --- 社交需求自然衰减 ---
            needs.social -= 0.3 * dt

            # --- 极端饥饿/口渴惩罚 ---
            if needs.thirst > 80:
                needs.energy -= 5.0 * dt
            if needs.hunger > 80:
                needs.energy -= 2.0 * dt

            needs._clamp_all()
