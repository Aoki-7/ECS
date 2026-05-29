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


def _clamp_value(value: float, min_v: float, max_v: float) -> float:
    value = round(value, 2)
    return max(min_v, min(value, max_v))


class PhysiologyNeedsHelper:
    """生理需求修改辅助类（ECS：逻辑放在 System 层）"""

    @staticmethod
    def add_hunger(needs, value: float):
        needs.hunger = _clamp_value(needs.hunger + value, 0.0, needs.max_hunger)

    @staticmethod
    def add_thirst(needs, value: float):
        needs.thirst = _clamp_value(needs.thirst + value, 0.0, needs.max_thirst)

    @staticmethod
    def add_energy(needs, value: float):
        needs.energy = _clamp_value(needs.energy + value, 0.0, needs.max_energy)

    @staticmethod
    def add_fatigue(needs, value: float):
        needs.fatigue = _clamp_value(needs.fatigue + value, 0.0, needs.max_fatigue)

    @staticmethod
    def add_social(needs, value: float):
        needs.social = _clamp_value(needs.social + value, 0.0, needs.max_social)

    @staticmethod
    def add_comfort(needs, value: float):
        needs.comfort = _clamp_value(needs.comfort + value, 0.0, needs.max_comfort)



