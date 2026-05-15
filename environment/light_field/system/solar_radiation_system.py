#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:solar_radiation_system.py
@说明:太阳辐射系统
@时间:2026/03/11 14:32:24
@作者:Sherry
@版本:1.0
'''




import math
from core.system import System
from core.world import World

from environment.light_field.components.solar_radiation_component import SolarRadiationComponent
from environment.light_field.components.solar_position_component import SolarPositionComponent

class SolarRadiationSystem(System):
    """根据太阳位置进行计算"""
    def update(self, world: World, delta_hour: float):

        solar_pos, radiation = world._world_entity.get_components(
            SolarPositionComponent,
            SolarRadiationComponent
        )

        solar_pos: SolarPositionComponent
        radiation: SolarRadiationComponent
        
        elevation = solar_pos.elevation

        if elevation <= 0:
            radiation.toa_radiation = 0.0
            return

        sin_elev = math.sin(math.radians(elevation))

        radiation.toa_radiation = (
            radiation.solar_constant * sin_elev
        )