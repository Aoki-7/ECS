#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
物理天气组件

存储纯粹连续物理量，不包含任何离散天气状态。
所有天气状态标签由 weather_classifier 从物理量实时推导。

【设计原则】
1. 仅存连续物理量 — 无枚举、无状态机
2. 无演化逻辑 — 所有更新由 PhysicalWeatherSystem 完成
3. 天气标签「推导而非存储」— 随查随算，永不缓存
"""

from dataclasses import dataclass, field
from typing import Optional

from core.component import Component


@dataclass
class PhysicalWeatherComponent(Component):
    """
    物理天气组件

    存储当前时刻的所有连续物理量。
    初始值代表「一个温和的春日早晨」。

    字段说明：
        temperature:        气温 (°C), 约 -30 ~ 50
        pressure:           气压 (hPa), 约 950 ~ 1060
        absolute_humidity:  绝对湿度 (g/m³), 约 0.1 ~ 35
        relative_humidity:  相对湿度 (0~1), 自动由 absolute_humidity 和 temperature 计算
        cloud_cover:        总云量 (0~1), 0=晴空, 1=完全覆盖
        precipitation_rate: 降水速率 (mm/h), 0=无降水
        wind_speed:         风速 (m/s), 约 0 ~ 50
    """

    # ── 核心物理量 ──
    temperature: float = 18.0
    pressure: float = 1015.0
    absolute_humidity: float = 7.5
    relative_humidity: float = 0.45
    cloud_cover: float = 0.15
    precipitation_rate: float = 0.0
    wind_speed: float = 2.0

    # ── 内部状态（系统演化使用） ──
    # 温度噪声累积值
    _temp_noise: float = 0.0
    # 气压相位偏移（小时）
    _pressure_phase: float = 0.0
    # 风速噪声累积值
    _wind_noise: float = 0.0

    # ── 调试/诊断信息 ──
    # 各物理量的变化速率（每小时），供调试查看
    debug_info: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "temperature": round(self.temperature, 2),
            "pressure": round(self.pressure, 2),
            "absolute_humidity": round(self.absolute_humidity, 3),
            "relative_humidity": round(self.relative_humidity, 4),
            "cloud_cover": round(self.cloud_cover, 4),
            "precipitation_rate": round(self.precipitation_rate, 4),
            "wind_speed": round(self.wind_speed, 2),
        }

    def __repr__(self) -> str:
        return (
            f"PhysicalWeather("
            f"T={self.temperature:.1f}°C, "
            f"P={self.pressure:.0f}hPa, "
            f"RH={self.relative_humidity:.1%}, "
            f"AH={self.absolute_humidity:.2f}g/m³, "
            f"cloud={self.cloud_cover:.0%}, "
            f"rain={self.precipitation_rate:.2f}mm/h, "
            f"wind={self.wind_speed:.1f}m/s"
            f")"
        )