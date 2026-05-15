#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:temperature_system.py
@说明:体温系统
@时间:2026/03/21 22:04:21
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World


from physiology.components.physiology_component import PhysiologyComponent
from physiology.components.temperature_component import TemperatureComponent


class TemperatureSystem(System):

    def update(self, world: World, dt: float):
        for entity, [temp, phys] in world.get_components(
            TemperatureComponent, PhysiologyComponent
        ):
            diff = abs(temp.body_temp - temp.optimal_temp)

            if diff > 2:
                # 体温异常 → 消耗能量
                phys.stats["energy"].value -= diff * 0.05 * dt