#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
光场系统模块 — 辐射传输计算

包含：
    - LightFieldSystem             : 主辐射计算（直射+散射→地表总辐射）
    - SolarPositionSystem          : 太阳位置计算（天文公式）
    - SolarRadiationSystem         : TOA 辐射计算（太阳常数+日地距离修正）
    - LightAtmosphereCouplingSystem: 大气散射参数更新（云量+气溶胶→光学厚度）

计算流程：
    SolarPositionSystem → SolarRadiationSystem → LightAtmosphereCouplingSystem
    → LightFieldSystem
"""

from .uv_system import UVSystem

__all__ = ['UVSystem']
