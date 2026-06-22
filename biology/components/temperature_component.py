#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:temperature_component.py
@说明:温度需求组件 - 纯数据版
'''

from dataclasses import dataclass
from core.component import Component

@dataclass(slots=True)
class TemperatureComponent(Component):
    """
    温度需求组件 - 纯数据版
    
    Attributes:
        body_temperature: 体温 °C
        comfort_min: 舒适温度下限
        comfort_max: 舒适温度上限
        discomfort: 不舒适度 (-50~+50, 0=舒适)
    """
    body_temperature: float = 37.0      # 体温 °C
    comfort_min: float = 20.0           # 舒适下限
    comfort_max: float = 26.0           # 舒适上限
    discomfort: float = 0.0             # 不舒适度
    
    def __post_init__(self):
        # 计算不舒适度
        if self.body_temperature < self.comfort_min:
            self.discomfort = self.comfort_min - self.body_temperature
        elif self.body_temperature > self.comfort_max:
            self.discomfort = self.body_temperature - self.comfort_max
        else:
            self.discomfort = 0.0
