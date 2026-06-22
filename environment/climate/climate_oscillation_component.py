#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:climate_oscillation_component.py
@说明:气候震荡组件
@时间:2026/03/14 11:16:25
@作者:Sherry
@版本:1.0
'''


"""
气候震荡组件（Climate Oscillation Component）

用于描述正在发生的气候震荡事件。

气候震荡是持续数月到数千年的大型气候异常现象，
会对温度、降水、气压和风场产生系统性影响。

典型示例：

- ENSO（厄尔尼诺 / 拉尼娜）
- PDO（太平洋年代际振荡）
- AMO（大西洋多年代际振荡）
- 冰期
- 间冰期
- 火山冬天
- 撞击冬天

该组件仅记录震荡产生的气候偏移量，
具体演化逻辑由 ClimateSystem 负责更新。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass
class ClimateOscillationComponent(Component):
    """
    气候震荡状态

    表示一个正在生效的气候震荡事件，
    其影响会叠加到基础气候和天气系统上。
    """

    # 震荡类型标识
    # 例如：ENSO、PDO、ICE_AGE、VOLCANIC_WINTER
    oscillation_type: str = "ENSO"

    # 温度异常值（°C）
    # 正值表示增温，负值表示降温。
    temperature_anomaly: float = 0.0

    # 降水异常值
    # 正值表示更湿润，负值表示更干旱。
    precipitation_anomaly: float = 0.0

    # 风场异常强度
    # 用于影响风速、风向等天气系统参数。
    wind_anomaly: float = 0.0

    # 气压异常强度
    # 用于影响高压、低压及天气变化趋势。
    pressure_anomaly: float = 0.0

    # 剩余持续时间（天）
    # 当减至 0 时，震荡事件结束。
    remaining_days: int = 0