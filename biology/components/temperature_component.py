#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:temperature_component.py
@说明:体感温度组件
@时间:2026/05/29
@版本:1.0
'''

# 已从 human/components/physiological/temperature_component.py 迁移至此
# 向后兼容导入: from human.components.physiological.temperature_component import TemperatureComponent
from dataclasses import dataclass
from core.component import Component


@dataclass
class TemperatureComponent(Component):
    """
    体感温度组件
    存储实体核心体温和热/冷应激状态
    """
    body_temperature: float = 37.0      # 核心体温 °C
    heat_stress: float = 0.0            # 热应激 0-100
    cold_stress: float = 0.0            # 冷应激 0-100
    is_heatstroke: bool = False
    is_frostbite: bool = False
