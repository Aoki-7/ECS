#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:hydration_system.py
@说明:体液系统
@时间:2026/03/21 21:57:47
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World
from physiology.components.hydration_component import HydrationComponent
from physiology.components.physiology_component import PhysiologyComponent


class HydrationSystem(System):
    tick_interval = 20  # 每20帧执行一次

    def update(self, world: World, dt: float):
        for entity, [hydro, phys] in world.get_components(
            HydrationComponent, PhysiologyComponent
        ):
            hydro.water_level -= hydro.dehydration_rate * dt

            # 映射到 thirst
            phys.stats["thirst"].value = 100 - hydro.water_level

            # 脱水惩罚
            if hydro.water_level < 30:
                phys.stats["energy"].value -= 0.2 * dt