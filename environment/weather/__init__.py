#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""天气模块 - 负责管理大气层中的天气过程"""

# ── 组件 ──
from .components.weather_component import WeatherComponent, saturated_vapor_pressure
from .components.weather_modifier_component import (
    WeatherEventTagComponent,
    LifetimeComponent,
    WeatherModifierComponent,
)

# ── 系统 ──
from .systems.cloud_system import CloudSystem, CloudLayer, total_cloud_cover_to_sky_state
from .systems.weather_system import WeatherSystem
from .systems.weather_event_system import WeatherEventSystem
from .systems.weather_lifetime_system import WeatherLifetimeSystem

# ── 工厂 ──
from .weather_event_factory import WeatherEventFactory, WeatherEventTemplates

# ── 配置枚举与状态 ──
from .config.weather_types import (
    SkyState,
    PrecipitationType,
    PrecipitationIntensity,
    VisibilityState,
    WindLevel,
    ExtremeWeather,
    WeatherState,
)

# ── 气候耦合 ──
from .config.climate_coupling import (
    AtmosphericForcing,
    PressureSystem,
    AtmosphericForcingModifier,
    PrecipitationCondition,
    calculate_atmospheric_stability,
    calculate_precipitation_probability,
    compute_precipitation_intensity,
    temp_to_sky,
    get_solar_elevation,
)

__all__ = [
    # 组件
    "WeatherComponent",
    "saturated_vapor_pressure",
    "WeatherEventTagComponent",
    "LifetimeComponent",
    "WeatherModifierComponent",
    # 系统
    "CloudSystem",
    "CloudLayer",
    "total_cloud_cover_to_sky_state",
    "WeatherSystem",
    "WeatherEventSystem",
    "WeatherLifetimeSystem",
    # 工厂
    "WeatherEventFactory",
    "WeatherEventTemplates",
    # 枚举 & 状态
    "SkyState",
    "PrecipitationType",
    "PrecipitationIntensity",
    "VisibilityState",
    "WindLevel",
    "ExtremeWeather",
    "WeatherState",
    # 气候耦合
    "AtmosphericForcing",
    "PressureSystem",
    "AtmosphericForcingModifier",
    "PrecipitationCondition",
    "calculate_atmospheric_stability",
    "calculate_precipitation_probability",
    "compute_precipitation_intensity",
    "temp_to_sky",
    "get_solar_elevation",
]
