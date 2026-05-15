
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:soil_temperature_component.py
@说明:土壤温度
@时间:2026/03/09 09:33:33
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass
class SoilTemperatureComponent(Component):
    """
    土壤温度

    来源：
    - Atmosphere
    - LightField
    影响：
    - 植物生长效率
    """
    temperature: float = 15.0