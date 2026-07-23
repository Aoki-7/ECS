#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:atmosphere_component.py
@说明:大气组件 v3.0 - 精简版

v3.0 变更:
- 从 886 字段精简至 ~50 核心字段
- 移除土壤/水文/化学/植被/放射性等不属于大气层的字段
- 保留大气物理、天气、空气质量核心字段
- 向后兼容: 通过 __getattr__ 动态返回默认值 0.0
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component

@dataclass(slots=False)
class AtmosphereComponent(Component):
    """
    大气组件 - 精简版
    仅存储大气层核心物理参数。
    """
    # === 基本参数 (5) ===
    pressure: float = 101.325           # 气压 hPa
    temperature: float = 20.0           # 温度 °C
    humidity: float = 0.5               # 相对湿度 0-1
    altitude: float = 0.0               # 海拔 m
    air_density: float = 1.225          # 空气密度 kg/m³

    # === 气体成分 (4) ===
    oxygen_level: float = 0.21          # 氧气体积分数
    co2_ratio: float = 0.0004           # CO₂ 体积分数 (400ppm)
    nitrogen_level: float = 0.78        # 氮气体积分数
    oxygen_ratio: float = 0.21          # 氧气体积分数 (兼容)

    # === 风场 (2) ===
    wind_speed: float = 0.0             # 风速 m/s
    wind_direction: float = 0.0         # 风向 °

    # === 云与降水 (2) ===
    cloud_cover: float = 0.0            # 云量 0-1
    precipitation_rate: float = 0.0     # 降水率 mm/h

    # === 辐射 (4) ===
    solar_radiation: float = 0.0        # 太阳辐射 W/m²
    net_radiation: float = 0.0          # 净辐射 W/m²
    albedo: float = 0.2                 # 反照率 0-1
    emissivity: float = 0.95            # 发射率 0-1

    # === 热通量 (3) ===
    sensible_heat_flux: float = 0.0     # 感热通量 W/m²
    latent_heat_flux: float = 0.0       # 潜热通量 W/m²
    ground_heat_flux: float = 0.0       # 地热通量 W/m²

    # === 空气质量 (8) ===
    pollution_level: float = 0.0        # 综合污染指数
    particulate_matter: float = 0.0       # 颗粒物浓度 µg/m³
    pm25: float = 0.0                   # PM2.5 µg/m³
    pm10: float = 0.0                   # PM10 µg/m³
    co_concentration: float = 0.0       # CO 浓度 ppm
    o3_concentration: float = 0.0       # O₃ 浓度 ppm
    no2_level: float = 0.0              # NO₂ 浓度 ppm
    so2_level: float = 0.0              # SO₂ 浓度 ppm
    aqi: float = 0.0                    # 空气质量指数
    
    # === 兼容字段 (测试用) ===
    no2_ppm: float = 0.0                # NO₂ ppm (兼容)
    so2_ppm: float = 0.0                # SO₂ ppm (兼容)
    o3_ppm: float = 0.0                 # O₃ ppm (兼容)
    co_ppm: float = 0.0                 # CO ppm (兼容)

    # === 能见度与光学 (2) ===
    visibility: float = 10.0            # 能见度 km
    uv_index: float = 0.0               # 紫外线指数

    # === 水汽相关 (5) ===
    dew_point: float = 10.0             # 露点 °C
    vapor_pressure: float = 2.0         # 水汽压 hPa
    mixing_ratio: float = 0.01          # 混合比 g/kg
    relative_humidity: float = 0.5      # 相对湿度 (兼容)
    absolute_humidity: float = 0.01     # 绝对湿度 g/m³

    # === 派生指数 (3) ===
    heat_index: float = 20.0            # 热指数 °C
    wind_chill: float = 20.0            # 风寒指数 °C
    wet_bulb_temperature: float = 15.0  # 湿球温度 °C

    # === 气压趋势 (2) ===
    pressure_tendency: float = 0.0      # 气压趋势 hPa/h
    pressure_change_3h: float = 0.0     # 3小时变压 hPa

    # === 历史记录 ===
    atmosphere_history: List[Dict] = field(default_factory=list)

    # === 向后兼容: 动态属性返回默认值 ===
    def __getattr__(self, name: str):
        """动态返回 0.0 以兼容旧代码访问已移除字段"""
        return 0.0