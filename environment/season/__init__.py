#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
季节模块 — 天文季节驱动

职责：
    - SeasonComponent: 存储当前天文季节参数（太阳赤纬角、日长、年份进度）
    - SeasonSystem: 根据时间推进计算天文参数，驱动季节变化
    - 为 SolarPositionSystem 和 ClimateSystem 提供输入

设计特点：
    - 不存储离散季节标签（春/夏/秋/冬），只存储连续天文参数
    - 季节体感由 physics_weather/ 的物理量实时推导
    - 支持任意纬度的季节差异（赤道日长变化小，极地变化大）
"""
