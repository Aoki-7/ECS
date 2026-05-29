#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:hunger_system.py
@说明:饥饿系统（拆分自 PhysiologyNeedsSystem）
@时间:2026/05/29
@版本:2.0
'''

from core.system import System
from core.world import World

from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType


class HungerSystem(System):
    """
    饥饿系统
    只负责饥饿值的自然增长，代谢受睡眠状态影响
    """

    BASE_HUNGER_RATE = 4.0   # 基础饥饿增长速率 /小时

    def update(self, world: World, dt: float):
        for entity, (needs,) in world.get_components(PhysiologyNeedsComponent):
            needs: PhysiologyNeedsComponent

            # 检测睡眠状态
            action = world.get_component(entity, ActionComponent)
            is_sleeping = (
                action is not None
                and action.current_action == ActionType.SLEEP
            )
            metabolic_mult = 0.2 if is_sleeping else 1.0

            # 饥饿增长
            hunger_rate = self.BASE_HUNGER_RATE * metabolic_mult * dt
            needs.hunger = min(needs.max_hunger, needs.hunger + hunger_rate)
