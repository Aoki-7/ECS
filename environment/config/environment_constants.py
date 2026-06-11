#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境模块常量

v3.2 优化 — 集中管理环境模块所有魔法值
"""

# ==================== 光照 ====================
DEFAULT_PAR = 300.0              # μmol/m²/s
DEFAULT_PHOTOPERIOD = 12.0       # 小时
DAYTIME_PAR_THRESHOLD = 50.0     # 判断白天的 PAR 阈值

# ==================== 温度 ====================
DEFAULT_AIR_TEMP = 25.0          # ℃
DEFAULT_SOIL_TEMP = 22.0         # ℃
DEFAULT_TEMP_DIFF = 5.0          # 昼夜温差 ℃

# ==================== 水分 ====================
DEFAULT_SOIL_MOISTURE = 0.35     # 0~1
DEFAULT_FIELD_CAPACITY = 0.45    # 田间持水量
DEFAULT_WILTING_POINT = 0.15     # 凋萎点
DEFAULT_AIR_HUMIDITY = 0.6       # 相对湿度
DEFAULT_VPD = 1.2                # kPa

# ==================== 气体 ====================
DEFAULT_CO2 = 420.0              # ppm
DEFAULT_O2 = 21.0                # %

# ==================== 土壤 ====================
DEFAULT_SOIL_PH = 6.5
DEFAULT_SOIL_EC = 1.5            # mS/cm
DEFAULT_NITROGEN = 50.0          # mg/kg
DEFAULT_PHOSPHORUS = 20.0        # mg/kg
DEFAULT_POTASSIUM = 60.0         # mg/kg

# ==================== 物理 ====================
DEFAULT_WIND_SPEED = 0.5         # m/s
DEFAULT_RAINFALL = 0.0           # mm/day

# ==================== 连续统系统 ====================
THERMAL_DIFFUSION_COEFF = 0.15
HUMIDITY_DIFFUSION_COEFF = 0.08
WATER_FLOW_COEFF = 0.05
ADVECTION_COEFF = 0.10
RECOVERY_RATE_BASE = 0.02

# CFL 条件：diff_coeff * dt < 0.5
MAX_DIFFUSION_COEFF = 0.5

# ==================== 季节 ====================
DAYS_PER_SEASON = 90
SEASONS = ["spring", "summer", "autumn", "winter"]

# ==================== 天气 ====================
RAIN_EVAPORATION_RATE = 0.05
CLOUD_FORMATION_THRESHOLD = 0.7
STORM_WIND_THRESHOLD = 15.0      # m/s
