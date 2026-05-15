#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:soil_builder.py
@说明:水土模块构建器
@时间:2026/03/11 11:33:14
@作者:Sherry
@版本:1.0
'''



from core.world import World


from environment.soil.components.soil_fertility_component import SoilFertilityComponent
from environment.soil.components.soil_moisture_component import SoilMoistureComponent
from environment.soil.components.soil_quality_component import SoilQualityComponent
from environment.soil.components.soil_temperature_component import SoilTemperatureComponent

from environment.soil.systems.soil_fertility_system import SoilFertilitySystem
from environment.soil.systems.soil_water_balance_system import SoilWaterBalanceSystem
from environment.soil.systems.soil_temperature_system import SoilTemperatureSystem


class SoilBuilder:
    @staticmethod
    def build(world: World, profile = None):
        """
        根据水土配置表创建水土组件并初始化状态
        """
        world._world_entity.add_components(SoilFertilityComponent(), SoilMoistureComponent(), SoilQualityComponent(), SoilTemperatureComponent())

        systems = [SoilFertilitySystem(), SoilWaterBalanceSystem(), SoilTemperatureSystem()]

        return systems
