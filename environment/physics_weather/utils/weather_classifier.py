#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
天气状态分类器

从 PhysicalWeatherComponent 的连续物理量实时推导离散天气状态标签。
核心原则：天气标签「推导而非存储」— 每次调用都根据当前物理量重新计算。

此模块无副作用、无状态，是纯函数。
"""

from dataclasses import dataclass
from typing import Optional

from environment.physics_weather.config.weather_thresholds import (
    CloudCoverLevel,
    PrecipitationType,
    PrecipitationIntensity,
    WindLevel,
    VisibilityState,
    CLOUD_COVER_THRESHOLDS,
    PRECIP_RATE_TO_INTENSITY,
    WIND_SPEED_TO_LEVEL,
    SNOW_TEMP_THRESHOLD,
    SLEET_TEMP_UPPER,
    FOG_RH_THRESHOLD,
    DENSE_FOG_RH_THRESHOLD,
    HAZE_RH_LOWER,
    HAZE_RH_UPPER,
    PRECIP_VISIBILITY_MAP,
)


@dataclass
class DerivedWeatherState:
    """
    从物理量推导出的天气状态标签。
    
    所有字段均为只读语义，由 classify() 一次性计算返回。
    """
    cloud_cover_level: CloudCoverLevel = CloudCoverLevel.CLEAR
    precipitation_type: PrecipitationType = PrecipitationType.NONE
    precipitation_intensity: PrecipitationIntensity = PrecipitationIntensity.NONE
    wind_level: WindLevel = WindLevel.CALM
    visibility: VisibilityState = VisibilityState.CLEAR

    @property
    def label(self) -> str:
        """
        人类可读的简短天气描述。
        优先级：降水 > 能见度 > 云量 > 风
        """
        if self.precipitation_type != PrecipitationType.NONE:
            return (
                f"{self.precipitation_intensity.value}_"
                f"{self.precipitation_type.value}"
            )
        if self.visibility != VisibilityState.CLEAR:
            return self.visibility.value
        return self.cloud_cover_level.value

    @property
    def full_label(self) -> str:
        """完整天气描述"""
        return (
            f"sky={self.cloud_cover_level.value}, "
            f"precip={self.precipitation_type.value}"
            f"({self.precipitation_intensity.value}), "
            f"wind={self.wind_level.value}, "
            f"vis={self.visibility.value}"
        )


# ====
# 单值分类函数
# ====

def classify_cloud_cover(cloud_cover: float) -> CloudCoverLevel:
    """从总云量 (0-1) 推导云量等级"""
    for threshold, level in CLOUD_COVER_THRESHOLDS:
        if cloud_cover < threshold:
            return level
    return CloudCoverLevel.OVERCAST


def classify_precipitation_type(
    precipitation_rate: float,
    temperature: float,
) -> PrecipitationType:
    """从降水速率和温度推导降水类型"""
    if precipitation_rate <= 0.0:
        return PrecipitationType.NONE
    if temperature < SNOW_TEMP_THRESHOLD:
        return PrecipitationType.SNOW
    if temperature < SLEET_TEMP_UPPER:
        return PrecipitationType.SLEET
    return PrecipitationType.RAIN


def classify_precipitation_intensity(
    precipitation_rate: float,
) -> PrecipitationIntensity:
    """从降水速率 (mm/h) 推导强度等级"""
    if precipitation_rate <= 0.0:
        return PrecipitationIntensity.NONE
    for threshold, intensity in PRECIP_RATE_TO_INTENSITY:
        if precipitation_rate <= threshold:
            return intensity
    return PrecipitationIntensity.EXTREME


def classify_wind_level(wind_speed: float) -> WindLevel:
    """从风速 (m/s) 推导风力等级"""
    for threshold, level in WIND_SPEED_TO_LEVEL:
        if wind_speed <= threshold:
            return level
    return WindLevel.STORM


def classify_visibility(
    relative_humidity: float,
    precipitation_rate: float,
    precipitation_intensity: PrecipitationIntensity,
) -> VisibilityState:
    """从相对湿度和降水推导能见度状态"""
    # 有降水时，能见度由降水强度决定
    if precipitation_rate > 0.0:
        return PRECIP_VISIBILITY_MAP.get(
            precipitation_intensity,
            VisibilityState.HAZE,
        )

    # 无降水时，能见度由相对湿度决定
    if relative_humidity >= DENSE_FOG_RH_THRESHOLD:
        return VisibilityState.DENSE_FOG
    if relative_humidity >= FOG_RH_THRESHOLD:
        return VisibilityState.FOG
    if relative_humidity >= HAZE_RH_LOWER:
        return VisibilityState.HAZE
    return VisibilityState.CLEAR


# ====
# 主分类入口
# ====

def classify(
    temperature: float,
    relative_humidity: float,
    cloud_cover: float,
    precipitation_rate: float,
    wind_speed: float,
) -> DerivedWeatherState:
    """
    从所有连续物理量推导完整天气状态。

    Args:
        temperature:        气温 (°C)
        relative_humidity:  相对湿度 (0~1)
        cloud_cover:        总云量 (0~1)
        precipitation_rate: 降水速率 (mm/h)
        wind_speed:         风速 (m/s)

    Returns:
        DerivedWeatherState — 所有天气状态标签
    """
    precip_type = classify_precipitation_type(precipitation_rate, temperature)
    precip_intensity = classify_precipitation_intensity(precipitation_rate)

    return DerivedWeatherState(
        cloud_cover_level=classify_cloud_cover(cloud_cover),
        precipitation_type=precip_type,
        precipitation_intensity=precip_intensity,
        wind_level=classify_wind_level(wind_speed),
        visibility=classify_visibility(
            relative_humidity,
            precipitation_rate,
            precip_intensity,
        ),
    )


def classify_from_component(weather_comp) -> DerivedWeatherState:
    """
    从 PhysicalWeatherComponent 实例推导天气状态。

    Args:
        weather_comp: PhysicalWeatherComponent 实例

    Returns:
        DerivedWeatherState
    """
    return classify(
        temperature=weather_comp.temperature,
        relative_humidity=weather_comp.relative_humidity,
        cloud_cover=weather_comp.cloud_cover,
        precipitation_rate=weather_comp.precipitation_rate,
        wind_speed=weather_comp.wind_speed,
    )
