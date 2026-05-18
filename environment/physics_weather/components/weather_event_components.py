#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@文件: weather_event_components.py
@说明: 极端天气事件组件 — 从 old weather/ 迁移至 physics_weather/
@时间: 2026/05/16
@作者: Sherry
@版本: 1.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from core.component import Component


# =
# 天气事件类型枚举
# =

class WeatherEventType(Enum):
    COLD_WAVE = "cold_wave"
    HEAT_WAVE = "heat_wave"
    STORM = "storm"
    DROUGHT = "drought"
    TYPHOON = "typhoon"
    SNOWSTORM = "snowstorm"

    @property
    def label(self) -> str:
        mapping = {
            WeatherEventType.COLD_WAVE: "寒潮",
            WeatherEventType.HEAT_WAVE: "热浪",
            WeatherEventType.STORM: "暴雨",
            WeatherEventType.DROUGHT: "干旱",
            WeatherEventType.TYPHOON: "台风",
            WeatherEventType.SNOWSTORM: "暴雪",
        }
        return mapping[self]


class WeatherSourceType(Enum):
    NATURAL = "natural"
    CLIMATE = "climate"
    DISASTER = "disaster"
    SCRIPTED = "scripted"
    PLAYER = "player"

    @property
    def label(self) -> str:
        mapping = {
            WeatherSourceType.NATURAL: "自然天气",
            WeatherSourceType.CLIMATE: "气候系统",
            WeatherSourceType.DISASTER: "灾害事件",
            WeatherSourceType.SCRIPTED: "剧情事件",
            WeatherSourceType.PLAYER: "玩家触发",
        }
        return mapping[self]


@dataclass
class ExtremeWeatherLifetimeComponent(Component):
    """极端天气生命周期组件"""
    remaining_hours: float

    def expired(self) -> bool:
        return self.remaining_hours <= 0


@dataclass
class WeatherEventTagComponent(Component):
    """天气事件标签组件"""
    event_type: WeatherEventType

    @property
    def name(self) -> str:
        return self.event_type.label

    @property
    def code(self) -> str:
        return self.event_type.value


@dataclass
class WeatherModifierComponent(Component):
    """天气变化组件"""
    duration_hours: float = 24.0
    temp_delta: float = 0.0
    humidity_delta: float = 0.0
    rainfall_delta: float = 0.0
    wind_speed_delta: Optional[float] = None
    pressure_delta: Optional[float] = None
    priority: int = field(default=100)

    def __post_init__(self):
        if self.duration_hours <= 0:
            raise ValueError("duration_hours must be > 0")
        if not -100 <= self.temp_delta <= 100:
            raise ValueError("temp_delta out of range")
        if not -10.0 <= self.humidity_delta <= 10.0:
            raise ValueError("humidity_delta must be in [-10, 10] (g/m³ absolute humidity)")
        if not -500 <= self.rainfall_delta <= 500:
            raise ValueError("rainfall_delta out of range")

    def is_extreme(self) -> bool:
        return (
            abs(self.temp_delta) >= 8
            or abs(self.rainfall_delta) >= 30
            or (self.wind_speed_delta is not None and abs(self.wind_speed_delta) >= 15)
        )

    def summary(self) -> str:
        return (
            f"WeatherModifier("
            f"temp={self.temp_delta:+.1f}°C, "
            f"humidity={self.humidity_delta:+.2f}, "
            f"rain={self.rainfall_delta:+.1f}mm/h, "
            f"wind={self.wind_speed_delta}, "
            f"pressure={self.pressure_delta})"
        )


@dataclass
class WeatherSourceComponent(Component):
    """天气来源组件"""
    source: WeatherSourceType

    @property
    def name(self) -> str:
        return self.source.label

    @property
    def code(self) -> str:
        return self.source.value
