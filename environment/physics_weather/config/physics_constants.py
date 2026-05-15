#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
物理天气常量与参数

包含所有物理常数、默认参数和演化系数。
所有可调参数集中在此，便于调参。
"""

import math

# ============================================================
# 🌡 温度演化参数
# ============================================================

# 日最高温出现的小时（通常 14:00）
DIURNAL_PEAK_HOUR: float = 14.0

# 日最低温出现的小时（通常日出前，约 5:00）
DIURNAL_TROUGH_HOUR: float = 5.0

# 默认日较差 (°C) — 实际值受云量调节
DEFAULT_DIURNAL_RANGE: float = 12.0

# 季节温度偏置幅度 (°C) — 夏季 +12, 冬季 -12
SEASONAL_TEMP_AMPLITUDE: float = 12.0

# 温度随机噪声标准差 (°C)
TEMP_NOISE_STD: float = 0.3

# 温度噪声回归系数（每步向 0 回归）
TEMP_NOISE_REGRESSION: float = 0.92

# 云量对日较差的阻尼系数
# 实际阻尼 = 1 - CLOUD_DAMPING_FACTOR * cloud_cover
# 云量 0 时无阻尼，云量 1 时阻尼最大
CLOUD_DAMPING_FACTOR: float = 0.6

# 海拔对温度的递减率 (°C/m)
ELEVATION_LAPSE_RATE: float = -0.0065

# ============================================================
# 🌀 气压演化参数
# ============================================================

# 平均海平面气压 (hPa)
STANDARD_PRESSURE: float = 1013.25

# 气压年周期幅度 (hPa)
PRESSURE_SEASONAL_AMP: float = 5.0

# 气压中周期（天气系统周期，小时）
PRESSURE_SYNOPTIC_PERIOD_HOURS: float = 120.0  # ~5天

# 气压中周期幅度 (hPa)
PRESSURE_SYNOPTIC_AMP: float = 15.0

# 气压随机噪声标准差 (hPa)
PRESSURE_NOISE_STD: float = 0.5

# 气压有效范围
PRESSURE_MIN: float = 950.0
PRESSURE_MAX: float = 1060.0

# ============================================================
# 💧 水汽演化参数
# ============================================================

# 水面蒸发系数 (g/m³ per hour per unit wind)
EVAPORATION_COEFFICIENT: float = 0.35

# 降水消耗系数 (mm⁻¹)
PRECIPITATION_CONSUMPTION: float = 0.3

# 水汽平流回归时间常数 (小时)
HUMIDITY_ADVECTION_TIMESCALE: float = 36.0

# 背景绝对湿度 (g/m³) — 平流漂移目标
# 中亚热带地区夏季可达 15-20 g/m³，冬季 5-8 g/m³
BACKGROUND_ABSOLUTE_HUMIDITY: float = 12.0

# 绝对湿度有效范围 (g/m³)
ABSOLUTE_HUMIDITY_MIN: float = 0.1
ABSOLUTE_HUMIDITY_MAX: float = 35.0

# ============================================================
# ☁️ 云量演化参数
# ============================================================

# 云形成的相对湿度阈值
# RH > CLOUD_FORMATION_RH_THRESHOLD → 云开始形成
CLOUD_FORMATION_RH_THRESHOLD: float = 0.55

# 云消散的相对湿度阈值
# RH < CLOUD_DISSIPATION_RH_THRESHOLD → 云开始消散
# 与形成阈值不同（滞后效应）
CLOUD_DISSIPATION_RH_THRESHOLD: float = 0.50

# 云形成速率系数 (per hour per unit RH excess)
CLOUD_FORMATION_RATE: float = 0.20

# 云消散速率系数 (per hour)
# 任何时候云量都有基线消散（晴空辐射冷却、下沉气流等）
CLOUD_DISSIPATION_BASE_RATE: float = 0.012

# RH 低于形成阈值时的额外消散系数 (per hour per unit RH deficit)
# 空气越干燥，消散越快
CLOUD_DISSIPATION_RH_RATE: float = 0.08

# 气团上升对云量的贡献系数
# 气压下降（低压系统）→ 上升气流 → 促进成云
CLOUD_PRESSURE_DROP_RATE: float = 0.020

# 云量最大增长率（每步）
CLOUD_MAX_GROWTH_RATE: float = 0.25

# 白天额外消散因子（太阳辐射促进云滴蒸发）
# 仅日出后到日落前生效
CLOUD_DAYTIME_DISSIPATION_FACTOR: float = 0.15

# ============================================================
# 🌧 降水演化参数
# ============================================================

# 降水的云量阈值
PRECIP_CLOUD_THRESHOLD: float = 0.55

# 降水的相对湿度阈值
PRECIP_RH_THRESHOLD: float = 0.80

# 基准降水量系数 (mm/h)
PRECIP_BASE_RATE: float = 6.0

# 降水消耗水汽的比例 (0-1)
PRECIP_HUMIDITY_DRAIN_FACTOR: float = 0.2

# ============================================================
# 🌬 风速演化参数
# ============================================================

# 基础风速 (m/s)
WIND_BASELINE: float = 2.0

# 风速的季节幅度 (m/s)
WIND_SEASONAL_AMP: float = 1.5

# 气压梯度对风速的贡献系数
WIND_PRESSURE_GRADIENT_COEFF: float = 0.08

# 风速随机噪声标准差 (m/s)
WIND_NOISE_STD: float = 0.4

# 风速回归系数（向基线回归）
WIND_REGRESSION_COEFF: float = 0.90

# 风速有效范围 (m/s)
WIND_MIN: float = 0.0
WIND_MAX: float = 50.0

# ============================================================
# 🧮 辅助物理函数
# ============================================================

def saturation_vapor_pressure(temperature_c: float) -> float:
    """
    Clausius-Clapeyron 方程（Magnus 近似）
    计算饱和水汽压 (hPa)
    
    Args:
        temperature_c: 温度 (°C)
    
    Returns:
        饱和水汽压 (hPa)
    """
    return 6.112 * math.exp(17.67 * temperature_c / (temperature_c + 243.5))


def saturation_absolute_humidity(temperature_c: float) -> float:
    """
    计算饱和绝对湿度 (g/m³)
    
    Args:
        temperature_c: 温度 (°C)
    
    Returns:
        饱和绝对湿度 (g/m³)
    """
    es = saturation_vapor_pressure(temperature_c)
    return es * 216.7 / (temperature_c + 273.15)


def relative_humidity(absolute_humidity: float, temperature_c: float) -> float:
    """
    计算相对湿度 (0-1)
    
    Args:
        absolute_humidity: 绝对湿度 (g/m³)
        temperature_c: 温度 (°C)
    
    Returns:
        相对湿度 (0-1), 钳制在 [0, 1]
    """
    ah_sat = saturation_absolute_humidity(temperature_c)
    if ah_sat <= 0:
        return 0.0
    return max(0.0, min(1.0, absolute_humidity / ah_sat))
