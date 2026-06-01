#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:disease_system.py
@说明:疾病系统
@时间:2026/03/21 22:20:58
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World

from physiology.components.physiology_component import PhysiologyComponent
from physiology.components.disease_component import InfectionLevelComponent

class DiseaseSystem(System):
    tick_interval = 20  # 每20帧执行一次

    def update(self, world: World, dt: float):
        for entity, [disease, phys] in world.get_components(
            InfectionLevelComponent, PhysiologyComponent
        ):
            if disease.infection_level > 0:
                phys.stats["energy"].value -= 0.2 * dt
                phys.stats["hunger"].value += 0.1 * dt