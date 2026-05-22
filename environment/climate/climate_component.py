#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
气候组件 — 长期趋势版

不再使用 ENSO 等硬编码相位。
所有气候波动由 Ornstein-Uhlenbeck 随机过程驱动，
模拟自然的长期记忆性和均值回归特性。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass
class ClimateComponent(Component):
    """
    气候趋势组件

    存储长期气候趋势的当前值，由 ClimateSystem 通过
    Ornstein-Uhlenbeck 过程更新。
    """

    # 温度长期趋势 (°C)
    temp_trend: float = 0.0

    # 湿度长期趋势 (0-1 偏置)
    humidity_trend: float = 0.0

    # 降雨长期趋势 (乘数)
    rainfall_trend: float = 1.0

    # 内部状态：OU 过程的当前速度
    _temp_velocity: float = 0.0
    _humidity_velocity: float = 0.0
    _rainfall_velocity: float = 0.0
