#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@文件: weather_event_components.py
@说明:
    physics_weather 极端天气事件组件

设计原则：
1. 事件是“诊断层”，不是直接天气结果
2. forcing 才是天气系统驱动力
3. 支持 ECS 高性能运行
4. 支持空间化天气系统
5. 支持事件生命周期演化
6. 支持未来 AI / 灾害 / 新闻 / NPC 扩展

@时间: 2026/05/18
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from core.component import Component


# ============================================================
# 天气事件类型
# ============================================================

class WeatherEventType(Enum):

    COLD_WAVE = "cold_wave"

    HEAT_WAVE = "heat_wave"

    STORM = "storm"

    DROUGHT = "drought"

    TYPHOON = "typhoon"

    SNOWSTORM = "snowstorm"


_EVENT_LABELS = {
    WeatherEventType.COLD_WAVE: "寒潮",
    WeatherEventType.HEAT_WAVE: "热浪",
    WeatherEventType.STORM: "暴雨",
    WeatherEventType.DROUGHT: "干旱",
    WeatherEventType.TYPHOON: "台风",
    WeatherEventType.SNOWSTORM: "暴雪",
}


# ============================================================
# 事件生命周期阶段
# ============================================================

class EventPhase(StrEnum):

    FORMING = "forming"

    MATURE = "mature"

    DECAYING = "decaying"

    DISSIPATED = "dissipated"


# ============================================================
# 事件来源类型
# ============================================================

class WeatherEventSourceType(StrEnum):

    NATURAL = "natural"

    CLIMATE_SYSTEM = "climate_system"

    SCRIPTED = "scripted"

    PLAYER = "player"

    DEBUG = "debug"


_SOURCE_LABELS = {
    WeatherEventSourceType.NATURAL: "自然生成",
    WeatherEventSourceType.CLIMATE_SYSTEM: "气候系统",
    WeatherEventSourceType.SCRIPTED: "剧情脚本",
    WeatherEventSourceType.PLAYER: "玩家触发",
    WeatherEventSourceType.DEBUG: "调试生成",
}


# ============================================================
# 事件诊断组件
# ============================================================

@dataclass(slots=True, frozen=True)
class WeatherEventDiagnosticComponent(Component):
    """
    天气事件诊断组件

    注意：
    该组件仅用于“识别天气模式”。

    不直接修改天气物理量。
    """

    event_id: int

    event_type: WeatherEventType

    severity: float = 0.5

    confidence: float = 1.0

    detected_hour: float = 0.0

    def __post_init__(self):

        if not 0.0 <= self.severity <= 1.0:
            raise ValueError("severity must be in [0,1]")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0,1]")

    @property
    def label(self) -> str:
        return _EVENT_LABELS[self.event_type]

    @property
    def code(self) -> str:
        return self.event_type.value


# ============================================================
# 生命周期组件
# ============================================================

@dataclass(slots=True)
class WeatherEventLifecycleComponent(Component):
    """
    天气事件生命周期
    """

    event_id: int

    total_duration_hours: float

    remaining_hours: float

    phase: EventPhase = EventPhase.FORMING

    intensity_progress: float = 0.0

    def __post_init__(self):

        if self.total_duration_hours <= 0:
            raise ValueError(
                "total_duration_hours must be > 0"
            )

        if self.remaining_hours < 0:
            raise ValueError(
                "remaining_hours must be >= 0"
            )

    @property
    def normalized_age(self) -> float:
        """
        生命周期进度
        """

        elapsed = (
            self.total_duration_hours
            - self.remaining_hours
        )

        return min(
            1.0,
            max(
                0.0,
                elapsed / self.total_duration_hours
            )
        )

    @property
    def expired(self) -> bool:
        return self.remaining_hours <= 0.0


# ============================================================
# 空间组件
# ============================================================

@dataclass(slots=True)
class WeatherEventSpatialComponent(Component):
    """
    天气事件空间属性
    """

    event_id: int

    center_x: float

    center_y: float

    radius_km: float

    velocity_x_kmh: float = 0.0

    velocity_y_kmh: float = 0.0

    pressure_center_hpa: Optional[float] = None

    def __post_init__(self):

        if self.radius_km <= 0:
            raise ValueError("radius_km must be > 0")


# ============================================================
# 大气 forcing 组件
# ============================================================

@dataclass(slots=True)
class AtmosphericForcingComponent(Component):
    """
    大气驱动力组件

    注意：
    不直接修改最终天气结果。

    而是作为：
        物理场演化输入
    """

    event_id: int

    # 热力 forcing
    thermal_forcing: float = 0.0

    # 水汽通量 forcing
    moisture_flux: float = 0.0

    # 气压 forcing
    pressure_forcing: float = 0.0

    # 风场 forcing
    wind_forcing_x: float = 0.0

    wind_forcing_y: float = 0.0

    # 云形成 forcing
    cloud_forcing: float = 0.0

    # 垂直运动 forcing
    vertical_motion_forcing: float = 0.0

    priority: int = 100

    def is_extreme(self) -> bool:

        return any([
            abs(self.thermal_forcing) > 8.0,
            abs(self.moisture_flux) > 5.0,
            abs(self.pressure_forcing) > 20.0,
            abs(self.wind_forcing_x) > 20.0,
            abs(self.wind_forcing_y) > 20.0,
        ])

    def __repr__(self):

        return (
            "AtmosphericForcing("
            f"thermal={self.thermal_forcing:+.2f}, "
            f"moisture={self.moisture_flux:+.2f}, "
            f"pressure={self.pressure_forcing:+.2f}, "
            f"wind_x={self.wind_forcing_x:+.2f}, "
            f"wind_y={self.wind_forcing_y:+.2f}, "
            f"cloud={self.cloud_forcing:+.2f}, "
            f"vertical={self.vertical_motion_forcing:+.2f}"
            ")"
        )


# ============================================================
# 事件来源组件
# ============================================================

@dataclass(slots=True, frozen=True)
class WeatherEventSourceComponent(Component):
    """
    天气事件来源组件
    """

    event_id: int

    source_type: WeatherEventSourceType

    @property
    def label(self) -> str:
        return _SOURCE_LABELS[self.source_type]

    @property
    def code(self) -> str:
        return self.source_type.value


# ============================================================
# 严重等级组件
# ============================================================

@dataclass(slots=True)
class WeatherEventSeverityComponent(Component):
    """
    天气事件严重等级
    """

    event_id: int

    severity: float

    category: int = 1

    damage_multiplier: float = 1.0

    emergency_level: int = 0

    def __post_init__(self):

        if not 0.0 <= self.severity <= 1.0:
            raise ValueError(
                "severity must be in [0,1]"
            )

        if self.category < 1:
            raise ValueError(
                "category must be >= 1"
            )

        if self.damage_multiplier < 0:
            raise ValueError(
                "damage_multiplier must be >= 0"
            )


# ============================================================
# 可选：天气事件统计组件
# ============================================================

@dataclass(slots=True)
class WeatherEventStatisticsComponent(Component):
    """
    天气事件统计信息
    """

    event_id: int

    max_temperature: Optional[float] = None

    min_pressure: Optional[float] = None

    max_wind_speed: Optional[float] = None

    accumulated_rainfall_mm: float = 0.0

    affected_population: int = 0

    affected_area_km2: float = 0.0


# ============================================================
# 导出
# ============================================================

__all__ = [

    # enum
    "WeatherEventType",
    "EventPhase",
    "WeatherEventSourceType",

    # components
    "WeatherEventDiagnosticComponent",
    "WeatherEventLifecycleComponent",
    "WeatherEventSpatialComponent",
    "AtmosphericForcingComponent",
    "WeatherEventSourceComponent",
    "WeatherEventSeverityComponent",
    "WeatherEventStatisticsComponent",
]