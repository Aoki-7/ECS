#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:thirst_system.py
@说明:口渴系统（拆分自 PhysiologyNeedsSystem）
@时间:2026/05/29
@版本:1.0
'''

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from core.components.action_component import ActionComponent, ActionType


class ThirstSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    口渴系统
    负责口渴值的自然增长及环境耦合（温度、湿度、干热）
    """

    BASE_THIRST_RATE = 3.5   # 基础口渴增长速率 /小时

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

            # 归一化饥饿值（用于耦合项）
            h = needs.hunger / needs.max_hunger
            hunger_to_thirst = 0.5 * h

            # 基础口渴增长 + 饥饿耦合
            thirst_rate = (
                self.BASE_THIRST_RATE + hunger_to_thirst
            ) * metabolic_mult * dt
            needs.thirst += thirst_rate

            # 环境耦合
            if env_is_valid:
                # 干热环境加剧口渴
                needs.thirst += 1.0 * env.water_stress_index * dt

                # 低湿度增加口渴
                if env.air_humidity < 0.3:
                    needs.thirst += 0.5 * dt

            # Clamp
            needs.thirst = max(0.0, min(needs.max_thirst, needs.thirst))
