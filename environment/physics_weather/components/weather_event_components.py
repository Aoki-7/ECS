#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@文件: weather_event_components.py
@说明:
    physics_weather 天气事件组件

设计原则：
1. 仅保留“天气事件”相关组件
2. 移除大气 forcing 系统
3. 不包含气候/大气动力学抽象
4. ECS 高性能组件化设计
5. 支持天气事件生命周期
6. 支持空间化天气事件

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
# 生命周期阶段
# ============================================================

class EventPhase(Enum):

    FORMING = "forming"

    MATURE = "mature"

    DECAYING = "decaying"

    DISSIPATED = "dissipated"


# ============================================================
# 事件来源类型
# ============================================================

class WeatherEventSourceType(Enum):

    NATURAL = "natural"

    SCRIPTED = "scripted"

    PLAYER = "player"

    DEBUG = "debug"


_SOURCE_LABELS = {
    WeatherEventSourceType.NATURAL: "自然生成",
    WeatherEventSourceType.SCRIPTED: "剧情脚本",
    WeatherEventSourceType.PLAYER: "玩家触发",
    WeatherEventSourceType.DEBUG: "调试生成",
}


# ============================================================
# 天气事件诊断组件
# ============================================================

@dataclass(slots=True, frozen=True)
class WeatherEventDiagnosticComponent(Component):
    """
    天气事件识别组件

    仅用于标识：
        当前存在什么天气事件

    不负责：
        物理模拟
        数值演化
        天气 forcing
    """

    event_id: int

    event_type: WeatherEventType

    severity: float = 0.5

    confidence: float = 1.0

    detected_hour: float = 0.0

    def __post_init__(self):

        if not 0.0 <= self.severity <= 1.0:
            raise ValueError(
                "severity must be in [0,1]"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "confidence must be in [0,1]"
            )

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

        if not 0.0 <= self.intensity_progress <= 1.0:
            raise ValueError(
                "intensity_progress must be in [0,1]"
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
        """
        是否结束
        """

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

    def __post_init__(self):

        if self.radius_km <= 0:
            raise ValueError(
                "radius_km must be > 0"
            )


# ============================================================
# 事件来源组件
# ============================================================

@dataclass(slots=True, frozen=True)
class WeatherEventSourceComponent(Component):
    """
    天气事件来源
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

        if self.emergency_level < 0:
            raise ValueError(
                "emergency_level must be >= 0"
            )


# ============================================================
# 天气事件统计组件
# ============================================================

@dataclass(slots=True)
class WeatherEventStatisticsComponent(Component):
    """
    天气事件统计信息
    """

    event_id: int

    max_temperature: Optional[float] = None

    min_temperature: Optional[float] = None

    max_wind_speed: Optional[float] = None

    accumulated_rainfall_mm: float = 0.0

    affected_population: int = 0

    affected_area_km2: float = 0.0

    def __post_init__(self):

        if self.accumulated_rainfall_mm < 0:
            raise ValueError(
                "accumulated_rainfall_mm must be >= 0"
            )

        if self.affected_population < 0:
            raise ValueError(
                "affected_population must be >= 0"
            )

        if self.affected_area_km2 < 0:
            raise ValueError(
                "affected_area_km2 must be >= 0"
            )


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
    "WeatherEventSourceComponent",
    "WeatherEventSeverityComponent",
    "WeatherEventStatisticsComponent",
]