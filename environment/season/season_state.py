#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
天文季节计算函数

不再使用春夏秋冬四季节枚举，所有季节效应由天文参数实时计算。
核心输入：day_of_year, latitude
核心输出：太阳赤纬角、日地距离因子、理论太阳辐射
"""

import math

# 地球轴倾角 (度)
AXIAL_TILT: float = 23.44

# 轨道偏心率导致的日地距离变化幅度 (~3.5%)
ORBITAL_ECCENTRICITY_FACTOR: float = 0.034

# 近日点大约在1月3日 (day 3)
PERIHELION_DAY: int = 3


def solar_declination(day_of_year: int) -> float:
    """
    太阳赤纬角：太阳光线与地球赤道面的夹角。
    夏至 (~day 173) 约 +23.44°，冬至 (~day 355) 约 -23.44°。
    """
    return AXIAL_TILT * math.sin(math.radians((360.0 / 365.0) * (day_of_year - 81)))


def earth_sun_distance_factor(day_of_year: int) -> float:
    """
    日地距离修正因子（对太阳常数的微调）。
    近日点时 > 1（辐射稍强），远日点时 < 1（辐射稍弱）。
    """
    angle = 2.0 * math.pi * (day_of_year - PERIHELION_DAY) / 365.0
    return 1.0 + ORBITAL_ECCENTRICITY_FACTOR * math.cos(angle)


def seasonal_insolation_factor(day_of_year: int, latitude: float = 35.0) -> float:
    """
    季节性太阳辐射因子，范围约 [-1, 1]。
    用于驱动温度季节变化，无需预定义季节名称。
    """
    dec = math.radians(solar_declination(day_of_year))
    lat = math.radians(latitude)
    # 简化：正午太阳高度角的正弦值作为辐射强度代理
    sin_elev_max = max(0.0, math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec))
    # 归一化到 [-1, 1] 区间，夏至≈1，冬至≈-1
    return (sin_elev_max - 0.35) / 0.35