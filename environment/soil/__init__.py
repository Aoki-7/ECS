"""
土壤子模块 — 水分平衡、温度、肥力、养分

依赖:
    - environment/
    - core/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
土壤模块 — 地表物质与养分循环

职责：
    - 管理土壤湿度、温度、肥力、养分（N/P/K）状态
    - 响应天气输入（降水→土壤水分，气温→土壤温度）
    - 为植物生长提供水分和养分约束

数据流：
    Weather → SoilMoisture (降水入渗、蒸发散失)
    Weather → SoilTemperature (热传导)
    SoilFertility + SoilMoisture → PlantGrowth (生物学)

子模块：
    - components/ : SoilMoisture, SoilFertility, SoilQuality, SoilTemperature
    - systems/    : SoilWaterBalanceSystem, SoilFertilitySystem, SoilTemperatureSystem, SoilSystem
"""

from .components.soil_fertility_component import SoilFertilityComponent
from .components.soil_moisture_component import SoilMoistureComponent
from .components.soil_quality_component import SoilQualityComponent
from .components.soil_temperature_component import SoilTemperatureComponent

__all__ = [
    "SoilFertilityComponent",
    "SoilMoistureComponent",
    "SoilQualityComponent",
    "SoilTemperatureComponent",
]


