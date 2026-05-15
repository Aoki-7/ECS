#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:fatigue_system.py
@说明:
@时间:2026/03/21 22:07:28
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World


from physiology.components.physiology_component import PhysiologyComponent
from physiology.components.fatigue_component import FatigueComponent


class FatigueSystem(System):

    def update(self, world: World, dt: float):
        for entity, [fatigue, phys] in world.get_components(
            FatigueComponent, PhysiologyComponent
        ):
            # 累积疲劳
            fatigue.fatigue += 0.1 * dt

            # energy 高 → 恢复
            if phys.stats["energy"].value > 60:
                fatigue.fatigue -= fatigue.recovery_rate * dt

            fatigue.fatigue = max(0, fatigue.fatigue)

            # 反作用
            if fatigue.fatigue > 50:
                phys.stats["energy"].value -= 0.1 * dt