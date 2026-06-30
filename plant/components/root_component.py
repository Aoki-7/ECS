#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
植物根系组件

描述植物根系的形态与功能特征，用于与土壤系统交互。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class PlantRootComponent(Component):
    """
    根系组件

    属性:
        root_depth: 根系深度 (cm)
        root_radius: 根系水平分布半径 (cm)
        water_absorption_rate: 吸水速率系数
        nutrient_absorption_rate: 养分吸收速率系数
        current_water_uptake: 当前 tick 的实际吸水量 (缓存)
    """
    root_depth: float = 5.0
    root_radius: float = 10.0
    water_absorption_rate: float = 1.0
    nutrient_absorption_rate: float = 1.0
    current_water_uptake: float = 0.0
