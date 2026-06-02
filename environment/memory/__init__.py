#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境记忆模块 — 历史数据存储与统计

职责：
    - EnvironmentMemoryComponent: 存储环境历史时间序列（温度、降水、光照等）
    - 提供滑动窗口统计（均值、方差、极值），供 WeatherEventSystem 做异常检测
    - 支持长期趋势分析（气候变暖/变干判定）

与 observation/ 的关系：
    - memory/ 存储原始历史数据
    - observation/ 基于历史数据做实时分析和状态推导
"""
