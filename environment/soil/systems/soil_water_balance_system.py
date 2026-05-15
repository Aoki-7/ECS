

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:soil_water_balance_system.py
@说明:土壤水分平衡系统
@时间:2026/03/09 09:34:33
@作者:Sherry
@版本:1.0
'''
from environment.weather.components.weather_component import WeatherComponent
from environment.soil.components.soil_moisture_component import SoilMoistureComponent

from core.world import World
from core.system import System

class SoilWaterBalanceSystem(System):
    """
        土壤水分平衡系统
        负责：
        - 降雨补给
        - 蒸发
        - 自然流失
    """
    def update(self, world: World, delta_hours: float):

        weather, soil = world._world_entity.get_components(WeatherComponent, SoilMoistureComponent)
        
        weather: WeatherComponent
        soil: SoilMoistureComponent

        # 降雨补给
        soil.moisture += weather.rainfall * 0.1

        # 蒸发
        soil.moisture -= weather.temperature * 0.001

        soil.moisture = max(0.0, min(soil.moisture, soil.capacity))