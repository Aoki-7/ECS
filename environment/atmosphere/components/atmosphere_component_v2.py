#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大气组件（完整版本）

维护大气的物理变量
"""

from dataclasses import dataclass
from core.component import Component


@dataclass
class AtmosphereComponent(Component):

    # ===============================
    # 气体系统
    # ===============================

    pressure: float = 1013.25      # 气压 hPa

    oxygen_ratio: float = 0.209
    co2_ratio: float = 0.00042

    aerosol: float = 0.0


    # ===============================
    # 水循环
    # ===============================

    water_vapor: float = 0.01      # 水汽含量 kg/kg


    # ===============================
    # 对流系统
    # ===============================

    convection_strength: float = 0.0
    turbulence: float = 0.0


    # ===============================
    # 云系统
    # ===============================

    cloud_cover: float = 0.0
    cloud_density: float = 0.0


    # ===============================
    # 风场
    # ===============================

    wind_speed: float = 0.0
    wind_direction: float = 0.0