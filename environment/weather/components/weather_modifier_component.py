#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@文件: weather_modifier_component.py
@说明: 天气变化组件系统（Enum 版本）
@时间: 2026/03/04
@作者: Sherry
@版本: 3.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from core.component import Component


# =========================================================
# 天气事件类型枚举
# =========================================================

class WeatherEventType(Enum):
    """
    天气事件类型
    """

    COLD_WAVE = "cold_wave"      # 寒潮
    HEAT_WAVE = "heat_wave"      # 热浪
    STORM = "storm"              # 暴风雨
    DROUGHT = "drought"          # 干旱
    TYPHOON = "typhoon"          # 台风
    SNOWSTORM = "snowstorm"      # 暴雪

    @property
    def label(self) -> str:
        """
        中文名称
        """

        mapping = {
            WeatherEventType.COLD_WAVE: "寒潮",
            WeatherEventType.HEAT_WAVE: "热浪",
            WeatherEventType.STORM: "暴雨",
            WeatherEventType.DROUGHT: "干旱",
            WeatherEventType.TYPHOON: "台风",
            WeatherEventType.SNOWSTORM: "暴雪",
        }

        return mapping[self]


# =========================================================
# 天气来源枚举
# =========================================================

class WeatherSourceType(Enum):
    """
    天气来源类型
    """

    NATURAL = "natural"      # 自然天气
    CLIMATE = "climate"      # 气候系统
    DISASTER = "disaster"    # 灾害事件
    SCRIPTED = "scripted"    # 剧情事件
    PLAYER = "player"        # 玩家触发

    @property
    def label(self) -> str:
        """
        中文名称
        """

        mapping = {
            WeatherSourceType.NATURAL: "自然天气",
            WeatherSourceType.CLIMATE: "气候系统",
            WeatherSourceType.DISASTER: "灾害事件",
            WeatherSourceType.SCRIPTED: "剧情事件",
            WeatherSourceType.PLAYER: "玩家触发",
        }

        return mapping[self]


# =========================================================
# 生命周期组件
# =========================================================

@dataclass
# =========================================================
# 极端天气生命周期组件
# =========================================================

@dataclass
class ExtremeWeatherLifetimeComponent(Component):
    """
    极端天气生命周期组件（Extreme Weather Lifetime Component）

    用于控制“极端天气事件实体”的存在周期。

    该组件通常附着于：
        - 寒潮实体
        - 台风实体
        - 暴雪实体
        - 干旱实体
        - 热浪实体
        - 暴风雨实体

    系统会在每次 update 时减少 remaining_hours，
    当 remaining_hours <= 0 时，
    说明该极端天气事件已经结束，
    系统应自动销毁对应天气事件实体。

    典型用途：
        - 控制天气持续时间
        - 控制临时环境修正生效时间
        - 控制灾害事件生命周期
        - 驱动天气事件自动消失

    示例：
        台风持续 48 小时：

        ExtremeWeatherLifetimeComponent(
            remaining_hours=48
        )

    工作流程：
        1. 创建极端天气事件实体
        2. 挂载 WeatherModifierComponent
        3. 挂载 WeatherEventTagComponent
        4. 挂载 ExtremeWeatherLifetimeComponent
        5. 系统每 tick 自动减少 remaining_hours
        6. 时间结束后自动删除实体

    Args:
        remaining_hours (float):
            极端天气剩余持续时间（单位：小时）

    Attributes:
        remaining_hours (float):
            剩余生命周期时间
    """

    remaining_hours: float

    def update(self, delta_hours: float) -> None:
        """
        更新生命周期时间

        Args:
            delta_hours (float):
                本次流逝时间（小时）
        """

        self.remaining_hours -= delta_hours

    @property
    def expired(self) -> bool:
        """
        判断极端天气是否结束

        Returns:
            bool:
                True  -> 已结束
                False -> 仍然生效
        """

        return self.remaining_hours <= 0


# =========================================================
# 天气事件标签组件
# =========================================================

@dataclass
class WeatherEventTagComponent(Component):
    """
    天气事件标签组件
    """

    event_type: WeatherEventType

    @property
    def name(self) -> str:
        """
        返回中文名称
        """

        return self.event_type.label

    @property
    def code(self) -> str:
        """
        返回内部编码
        """

        return self.event_type.value


# =========================================================
# 天气影响组件
# =========================================================

@dataclass
class WeatherModifierComponent(Component):
    """
    天气变化组件
    """

    # -------------------------
    # 基础环境影响
    # -------------------------

    duration_hours: float = 24.0
    temp_delta: float = 0.0
    humidity_delta: float = 0.0
    rainfall_delta: float = 0.0

    # -------------------------
    # 扩展环境影响
    # -------------------------

    wind_speed_delta: Optional[float] = None
    pressure_delta: Optional[float] = None

    # -------------------------
    # 优先级
    # -------------------------

    priority: int = field(default=100)

    # =====================================================
    # 参数校验
    # =====================================================

    def __post_init__(self):

        if self.duration_hours <= 0:
            raise ValueError("duration_hours 必须大于 0")

        if not -100 <= self.temp_delta <= 100:
            raise ValueError("temp_delta 数值异常")

        if not -1.0 <= self.humidity_delta <= 1.0:
            raise ValueError("humidity_delta 必须在 -1~1 之间")

        if not -500 <= self.rainfall_delta <= 500:
            raise ValueError("rainfall_delta 数值异常")

    # =====================================================
    # 逻辑方法
    # =====================================================

    def is_extreme(self) -> bool:
        """
        是否为极端天气
        """

        return (
            abs(self.temp_delta) >= 8
            or abs(self.rainfall_delta) >= 30
            or (
                self.wind_speed_delta is not None
                and abs(self.wind_speed_delta) >= 15
            )
        )

    def summary(self) -> str:
        """
        调试摘要
        """

        return (
            f"WeatherModifier("
            f"temp={self.temp_delta:+.1f}°C, "
            f"humidity={self.humidity_delta:+.2f}, "
            f"rain={self.rainfall_delta:+.1f}mm/h, "
            f"wind={self.wind_speed_delta}, "
            f"pressure={self.pressure_delta})"
        )


# =========================================================
# 天气来源组件
# =========================================================

@dataclass
class WeatherSourceComponent(Component):
    """
    天气来源组件
    """

    source: WeatherSourceType

    @property
    def name(self) -> str:
        """
        中文名称
        """

        return self.source.label

    @property
    def code(self) -> str:
        """
        内部编码
        """

        return self.source.value