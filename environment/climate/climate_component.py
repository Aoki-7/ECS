#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:climate_component.py
@说明:气候组件
@时间:2026/06/18 13:41:35
@作者:Sherry
@版本:2.0
'''


"""
气候组件（Climate Component）

用于保存世界当前的长期气候状态。

这些状态并不直接表示天气，而是影响天气生成的
长期气候趋势，例如持续变暖、长期干旱或多雨周期等。

气候趋势由 ClimateSystem 持续更新，
采用 Ornstein-Uhlenbeck（OU）随机过程模拟：

- 具有长期记忆性
- 会围绕平均状态波动
- 不会无限增长或衰减

V2 变更：
- 移除 OU 过程内部 velocity 状态，改为标准离散 OU 更新。
- 仅保留长期气候趋势字段。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass
class ClimateComponent(Component):
    """
    长期气候趋势数据

    保存当前世界的气候偏移量，
    供天气系统、生态系统和生物系统使用。

    数值越偏离默认值，说明当前气候状态越异常。
    """

    # 温度趋势偏移（单位：°C）
    # 正值表示整体偏暖，负值表示整体偏冷。
    temp_trend: float = 0.0

    # 湿度趋势偏移（范围建议：-1 ~ 1）
    # 正值表示环境更湿润，负值表示环境更干燥。
    humidity_trend: float = 0.0

    # 降雨趋势系数
    # 1.0 为正常水平；
    # 大于 1 表示降雨增强；
    # 小于 1 表示降雨减少。
    rainfall_trend: float = 1.0
