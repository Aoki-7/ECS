"""
光场包 — 太阳辐射、地表光照、直射/散射

依赖：
    - core/
    - space/
    - time_module/

版本：v4.0

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
光场模块 — 地表太阳辐射计算

职责：
    - 根据太阳位置、大气散射、云量遮挡、地形阴影计算地表光照
    - 为植物光合作用（biology/）提供能量输入
    - 为地表加热、蒸发、人类视觉提供光照数据

输入来源：
    - SeasonSystem     → 太阳高度角
    - PhysicsWeatherSystem → 云量遮挡
    - AtmosphereSystem → 散射参数
    - TerrainSystem    → 地形阴影
    - TimeSystem       → 昼夜变化

输出用途：
    - Vegetation（biology/） → 光合作用
    - SoilTemperatureSystem   → 地表加热
    - EvaporationSystem       → 蒸发驱动
    - Human/Animal Perception → 视觉范围修正

子模块：
    - components/ : LightFieldComponent, SolarPositionComponent, SolarRadiationComponent
    - system/     : LightFieldSystem（辐射传输计算）
    - systems/    : 光场主系统
"""

