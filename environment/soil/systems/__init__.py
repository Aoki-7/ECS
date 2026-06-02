#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
土壤系统模块 — 土壤状态更新逻辑

包含：
    - SoilSystem            : 土壤综合管理（养分循环、pH 缓冲）
    - SoilWaterBalanceSystem: 水分平衡（降水入渗、蒸发、植物蒸腾、地下水交换）
    - SoilTemperatureSystem : 土壤温度（大气热传导、植被遮蔽、水分比热）
    - SoilFertilitySystem   : 肥力更新（有机物分解、养分固定与释放）

输入来源：
    - physics_weather/ → 降水、气温
    - light_field/     → 地表加热
    - biology/         → 植物根系吸收、尸体分解补充
"""

from .soil_system import SoilSystem

__all__ = ['SoilSystem']
