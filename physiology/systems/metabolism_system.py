#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:metabolism_system.py
@说明:代谢系统
@时间:2026/03/21 21:49:51
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World
from physiology.components.physiology_component import PhysiologyComponent
from physiology.components.metabolism_component import MetabolismComponent


class MetabolismSystem(System):

    def update(self, world: World, dt: float):
        for entity, [phys, meta] in world.get_components(
            PhysiologyComponent, MetabolismComponent
        ):
            consumption = meta.basal_rate * meta.activity_multiplier

            # 消耗 energy
            phys.stats["energy"].value -= consumption * dt

            # 增加 hunger / thirst
            phys.stats["hunger"].value += 0.5 * consumption * dt
            phys.stats["thirst"].value += 0.7 * consumption * dt