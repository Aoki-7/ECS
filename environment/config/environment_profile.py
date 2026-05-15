









#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
环境配置对象

用于一次性描述一个区域的全部环境属性，
包括气候、天气、大气、光照、土壤等。

不同区域只需要定义不同 Profile。
"""

from dataclasses import dataclass


@dataclass
class EnvironmentProfile:

    # ===============================
    # 气候 Climate
    # ===============================

    avg_temp: float = 20
    temp_seasonal_amp: float = 10
    rainfall_yearly: float = 800
    humidity_avg: float = 0.6

    # ===============================
    # 天气 Weather
    # ===============================

    weather_noise: float = 2.0
    weather_state_hours: float = 6.0

    # ===============================
    # 大气 Atmosphere
    # ===============================

    pressure: float = 1013.25
    wind_speed: float = 2.0
    wind_direction: float = 0.0
    co2: float = 420
    oxygen: float = 0.21

    # ===============================
    # 光照 LightField
    # ===============================

    sunlight_base: float = 1.0
    sunlight_variance: float = 0.2

    # ===============================
    # 土壤 Soil
    # ===============================

    soil_moisture: float = 0.4
    soil_nutrients: float = 0.6

    # ===============================
    # 污染 Pollution
    # ===============================

    pollution: float = 0.0