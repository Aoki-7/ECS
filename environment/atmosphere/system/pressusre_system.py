


#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:pressusre_system.py
@说明:气压系统，主要受温度和密度影响
@时间:2026/03/07 11:35:03
@作者:Sherry
@版本:1.0
'''



from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent

class PressureSystem(System):
    """
    气压系统，主要受温度和密度影响
    """
    def update(self, world: World, delta_hours: float):

        for entity, [atm] in world.get_components(AtmosphereComponent):
            atm: AtmosphereComponent

            base = 1013.25

            temp_effect = (1.225 - atm.air_density) * 200

            atm.pressure = base + temp_effect