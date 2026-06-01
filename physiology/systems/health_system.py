#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:health_system.py
@说明:
@时间:2026/03/21 22:00:58
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World
from physiology.components.health_component import VitalityComponent
from physiology.components.physiology_component import PhysiologyComponent


class HealthSystem(System):
    tick_interval = 20  # 每20帧执行一次

    def update(self, world: World, dt: float):
        for entity, [health, phys] in world.get_components(
            VitalityComponent, PhysiologyComponent
        ):
            # 自动恢复（受 energy 影响）
            energy = phys.stats["energy"].value

            if energy > 50:
                health.hp += health.regen_rate * dt

            # 饥饿/口渴惩罚
            if phys.stats["hunger"].value > 80:
                health.hp -= 0.2 * dt

            if phys.stats["thirst"].value > 80:
                health.hp -= 0.3 * dt

            health.hp = max(0, min(health.hp, health.max_hp))