


#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:solar_position_system.py
@说明:太阳位置系统
@时间:2026/03/11 12:09:33
@作者:Sherry
@版本:1.0
'''



import math

from core.system import System
from core.world import World

from environment.light_field.components.solar_position_component import SolarPositionComponent

class SolarPositionSystem(System):
    """
    输入：
        Season
        Time
        Latitude
    输出：
        SolarPositionComponent
    """
    def update(self, world: World, delta_hour: float):
        time = world.get_time()

        solar_pos = world._world_entity.get_component(SolarPositionComponent)
        
        solar_pos: SolarPositionComponent

        # 获取当前是一年的第几天
        day = time.day_of_year

        # 地球轴倾角
        tilt = 23.44

        # 太阳赤纬角
        declination = tilt * math.sin(
            math.radians((360 / 365) * (day - 81))
        )

        # 假设固定纬度
        latitude = 35.0

        # 简化太阳高度
        elevation = 90 - abs(latitude - declination)

        solar_pos.elevation = max(elevation, 0.0)

        # 简化昼长
        solar_pos.day_length = 12 + 4 * math.sin(
            math.radians((360 / 365) * (day - 81))
        )

        solar_pos.azimuth = 180.0