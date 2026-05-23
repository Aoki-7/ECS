#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
天气状态分类器

从 PhysicalWeatherComponent 的连续物理量实时推导离散天气状态标签。
核心原则：天气标签「推导而非存储」— 每次调用都根据当前物理量重新计算。

此模块无副作用、无状态，是纯函数。

自适应版本：
    维护历史滑动窗口，基于统计分位数（percentile）动态计算阈值，
    使分类标签反映当地气候常态而非全球固定值。
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from collections import deque

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


# ============================================================
# 自适应分类器 — 基于历史统计分位数的动态阈值
# ============================================================

# 模块级历史滑动窗口
_HISTORY_WINDOW_SIZE = 720  # 约30天
_adaptive_history: Dict[str, deque] = {
    "cloud_cover": deque(maxlen=_HISTORY_WINDOW_SIZE),
    "precipitation_rate": deque(maxlen=_HISTORY_WINDOW_SIZE),
    "wind_speed": deque(maxlen=_HISTORY_WINDOW_SIZE),
    "relative_humidity": deque(maxlen=_HISTORY_WINDOW_SIZE),
    "temperature": deque(maxlen=_HISTORY_WINDOW_SIZE),
}


def reset_history():
    """重置历史窗口（测试用）"""
    for key in _adaptive_history:
        _adaptive_history[key].clear()


def _update_history(
    cloud_cover: float,
    precipitation_rate: float,
    wind_speed: float,
    relative_humidity: float,
    temperature: float,
):
    """更新历史滑动窗口"""
    _adaptive_history["cloud_cover"].append(cloud_cover)
    _adaptive_history["precipitation_rate"].append(precipitation_rate)
    _adaptive_history["wind_speed"].append(wind_speed)
    _adaptive_history["relative_humidity"].append(relative_humidity)
    _adaptive_history["temperature"].append(temperature)


def _percentile(values: List[float], p: float) -> float:
    """
    计算分位数（线性插值）。
    
    Args:
        values: 已排序的数值列表
        p: 分位点 (0~100)
    
    Returns:
        分位数值
    """
    if not values:
        return 0.0
    n = len(values)
    if n == 1:
        return values[0]
    # 使用 numpy 兼容的线性插值
    idx = (n - 1) * p / 100.0
    lower = int(idx)
    upper = lower + 1
    if upper >= n:
        return values[-1]
    weight = idx - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def _get_percentile(key: str, p: float, default: float) -> float:
    """从指定历史窗口获取分位数"""
    hist = list(_adaptive_history[key])
    if len(hist) < 48:  # 至少需要2天数据才使用动态阈值
        return default
    return _percentile(sorted(hist), p)


def classify_cloud_cover_adaptive(cloud_cover: float) -> CloudCoverLevel:
    """基于历史云量分布的动态云量等级分类"""
    p20 = _get_percentile("cloud_cover", 20, 0.05)
    p50 = _get_percentile("cloud_cover", 50, 0.25)
    p80 = _get_percentile("cloud_cover", 80, 0.50)

    if cloud_cover < p20:
        return CloudCoverLevel.CLEAR
    elif cloud_cover < p50:
        return CloudCoverLevel.PARTLY_CLOUDY
    elif cloud_cover < p80:
        return CloudCoverLevel.CLOUDY
    else:
        return CloudCoverLevel.OVERCAST


def classify_precipitation_type_adaptive(
    precipitation_rate: float,
    temperature: float,
) -> PrecipitationType:
    """基于历史温度分布的动态降水类型分类"""
    if precipitation_rate <= 0.0:
        return PrecipitationType.NONE

    mean_t = _get_percentile("temperature", 50, 5.0)
    p15_t = _get_percentile("temperature", 15, -2.0)

    # 动态阈值：极冷(< p15) → 雪, 偏冷(< mean) → 雨夹雪, 正常 → 雨
    if temperature < p15_t:
        return PrecipitationType.SNOW
    elif temperature < mean_t:
        return PrecipitationType.SLEET
    else:
        return PrecipitationType.RAIN


def classify_precipitation_intensity_adaptive(
    precipitation_rate: float,
) -> PrecipitationIntensity:
    """基于历史降水分布的动态强度分类"""
    if precipitation_rate <= 0.0:
        return PrecipitationIntensity.NONE

    p30 = _get_percentile("precipitation_rate", 30, 0.1)
    p60 = _get_percentile("precipitation_rate", 60, 2.5)
    p85 = _get_percentile("precipitation_rate", 85, 7.6)

    if precipitation_rate < p30:
        return PrecipitationIntensity.LIGHT
    elif precipitation_rate < p60:
        return PrecipitationIntensity.MODERATE
    elif precipitation_rate < p85:
        return PrecipitationIntensity.HEAVY
    else:
        return PrecipitationIntensity.EXTREME


def classify_wind_level_adaptive(wind_speed: float) -> WindLevel:
    """基于历史风速分布的动态风力等级分类"""
    p20 = _get_percentile("wind_speed", 20, 0.3)
    p45 = _get_percentile("wind_speed", 45, 1.5)
    p70 = _get_percentile("wind_speed", 70, 5.4)
    p88 = _get_percentile("wind_speed", 88, 10.7)

    if wind_speed < p20:
        return WindLevel.CALM
    elif wind_speed < p45:
        return WindLevel.BREEZE
    elif wind_speed < p70:
        return WindLevel.STRONG
    elif wind_speed < p88:
        return WindLevel.GALE
    else:
        return WindLevel.STORM


def classify_visibility_adaptive(
    relative_humidity: float,
    precipitation_rate: float,
    precipitation_intensity: PrecipitationIntensity,
) -> VisibilityState:
    """基于历史湿度分布的动态能见度分类"""
    # 有降水时，能见度由降水强度决定
    if precipitation_rate > 0.0:
        return PRECIP_VISIBILITY_MAP.get(
            precipitation_intensity,
            VisibilityState.HAZE,
        )

    # 无降水时，能见度由相对湿度分布决定
    p25 = _get_percentile("relative_humidity", 25, 0.75)
    p55 = _get_percentile("relative_humidity", 55, 0.93)
    p82 = _get_percentile("relative_humidity", 82, 0.97)

    if relative_humidity >= p82:
        return VisibilityState.DENSE_FOG
    elif relative_humidity >= p55:
        return VisibilityState.FOG
    elif relative_humidity >= p25:
        return VisibilityState.HAZE
    else:
        return VisibilityState.CLEAR


# ============================================================
# 主分类入口（自适应版本）
# ============================================================

def classify_adaptive(
    temperature: float,
    relative_humidity: float,
    cloud_cover: float,
    precipitation_rate: float,
    wind_speed: float,
) -> DerivedWeatherState:
    """
    自适应分类：先更新历史窗口，再基于统计分位数推导天气状态。
    
    当历史数据不足 48 小时时，自动回退到固定阈值。
    """
    _update_history(cloud_cover, precipitation_rate, wind_speed, relative_humidity, temperature)

    precip_type = classify_precipitation_type_adaptive(precipitation_rate, temperature)
    precip_intensity = classify_precipitation_intensity_adaptive(precipitation_rate)

    return DerivedWeatherState(
        cloud_cover_level=classify_cloud_cover_adaptive(cloud_cover),
        precipitation_type=precip_type,
        precipitation_intensity=precip_intensity,
        wind_level=classify_wind_level_adaptive(wind_speed),
        visibility=classify_visibility_adaptive(
            relative_humidity,
            precipitation_rate,
            precip_intensity,
        ),
    )


def classify_from_component_adaptive(weather_comp) -> DerivedWeatherState:
    """从 PhysicalWeatherComponent 实例自适应推导天气状态"""
    return classify_adaptive(
        temperature=weather_comp.temperature,
        relative_humidity=weather_comp.relative_humidity,
        cloud_cover=weather_comp.cloud_cover,
        precipitation_rate=weather_comp.precipitation_rate,
        wind_speed=weather_comp.wind_speed,
    )


# ============================================================
# 固定阈值版本（保留向后兼容）
# ============================================================

def classify_cloud_cover(cloud_cover: float) -> CloudCoverLevel:
    """从总云量 (0-1) 推导云量等级（固定阈值）"""
    for threshold, level in CLOUD_COVER_THRESHOLDS:
        if cloud_cover < threshold:
            return level
    return CloudCoverLevel.OVERCAST


def classify_precipitation_type(
    precipitation_rate: float,
    temperature: float,
) -> PrecipitationType:
    """从降水速率和温度推导降水类型（固定阈值）"""
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
    """从降水速率 (mm/h) 推导强度等级（固定阈值）"""
    if precipitation_rate <= 0.0:
        return PrecipitationIntensity.NONE
    for threshold, intensity in PRECIP_RATE_TO_INTENSITY:
        if precipitation_rate <= threshold:
            return intensity
    return PrecipitationIntensity.EXTREME


def classify_wind_level(wind_speed: float) -> WindLevel:
    """从风速 (m/s) 推导风力等级（固定阈值）"""
    for threshold, level in WIND_SPEED_TO_LEVEL:
        if wind_speed <= threshold:
            return level
    return WindLevel.STORM


def classify_visibility(
    relative_humidity: float,
    precipitation_rate: float,
    precipitation_intensity: PrecipitationIntensity,
) -> VisibilityState:
    """从相对湿度和降水推导能见度状态（固定阈值）"""
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


def classify(
    temperature: float,
    relative_humidity: float,
    cloud_cover: float,
    precipitation_rate: float,
    wind_speed: float,
) -> DerivedWeatherState:
    """
    从所有连续物理量推导完整天气状态（固定阈值版本）。
    纯函数，无历史依赖，向后兼容。
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
    """从 PhysicalWeatherComponent 实例推导天气状态（固定阈值版本）"""
    return classify(
        temperature=weather_comp.temperature,
        relative_humidity=weather_comp.relative_humidity,
        cloud_cover=weather_comp.cloud_cover,
        precipitation_rate=weather_comp.precipitation_rate,
        wind_speed=weather_comp.wind_speed,
    )
