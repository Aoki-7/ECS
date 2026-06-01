#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:metal_oxidation_system.py
@说明:金属氧化系统
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.0
'''

from core.system import System
from core.world import World

from resource.metal.components.metal_component import MetalComponent


class MetalOxidationSystem(System):
    tick_interval = 20  # 每20帧执行一次

    def update(self, world: World, dt: float):
        for entity, [metal] in world.get_components(MetalComponent):
            metal: MetalComponent
            # 更新金属氧化
            metal.update_oxidation(dt)