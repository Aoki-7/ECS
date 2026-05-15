<<<<<<< HEAD
=======


>>>>>>> 65a14767a91c763628f1030bcdd9bce57d718edc
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:soil_water_balance_system.py
@说明:土壤水分平衡系统
<<<<<<< HEAD
      已适配 PhysicalWeatherComponent（替代旧版 WeatherComponent）
@时间:2026/03/09 09:34:33
@作者:Sherry
@版本:2.0
'''

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
=======
@时间:2026/03/09 09:34:33
@作者:Sherry
@版本:1.0
'''
from environment.weather.components.weather_component import WeatherComponent
>>>>>>> 65a14767a91c763628f1030bcdd9bce57d718edc
from environment.soil.components.soil_moisture_component import SoilMoistureComponent

from core.world import World
from core.system import System

<<<<<<< HEAD

class SoilWaterBalanceSystem(System):
    """
    土壤水分平衡系统
    负责：
    - 降雨补给（来自 PhysicalWeatherComponent.precipitation_rate）
    - 蒸发（基于 PhysicalWeatherComponent.temperature 简化计算）
    - 自然流失
    """
    def update(self, world: World, delta_hours: float):

        weather, soil = world._world_entity.get_components(
            PhysicalWeatherComponent, SoilMoistureComponent,
        )

        weather: PhysicalWeatherComponent
        soil: SoilMoistureComponent

        # 降雨补给 (mm/h → 土壤湿度增量)
        soil.moisture += weather.precipitation_rate * 0.1 * delta_hours

        # 蒸发 (温度越高, 蒸发越快)
        soil.moisture -= weather.temperature * 0.001 * delta_hours

        soil.moisture = max(0.0, min(soil.moisture, soil.capacity))
=======
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
>>>>>>> 65a14767a91c763628f1030bcdd9bce57d718edc
