#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:toxicity_system.py
@说明:
@时间:2026/03/21 22:12:12
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World


from physiology.components.physiology_component import PhysiologyComponent
from physiology.components.toxicity_component import ToxicityComponent

class ToxicitySystem(System):
    tick_interval = 20  # 每20帧执行一次

    def update(self, world: World, dt: float):
        for entity, [tox, phys] in world.get_components(
            ToxicityComponent, PhysiologyComponent
        ):
            tox.toxin_level -= tox.decay_rate * dt
            tox.toxin_level = max(0, tox.toxin_level)

            # 毒素影响
            phys.stats["energy"].value -= tox.toxin_level * 0.01 * dt