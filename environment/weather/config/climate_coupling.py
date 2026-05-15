#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


# ==================== 大气强迫参数 ====================

@dataclass
class AtmosphericForcing:
    """大气强迫参数（驱动天气状态改变的外部因素）

    Args:
        solar_insolation: 日太阳辐射量 (0-1)
        latitude: 纬度 (-90 ~ 90 度)
        longitude: 经度
        elevation: 海拔高度 (米)
        distance_from_coast: 距海岸距离 (公里, 负值表示海洋上)
    """
    solar_insolation: float = 0.5
    latitude: float = field(default=35.0)
    longitude: float = field(default=120.0)
    elevation: float = field(default=0.0)
    distance_from_coast: float = field(default=50.0)

    def get_base_solar(self) -> float:
        """计算基础太阳辐射强度"""
        return max(0, math.cos(math.radians(90 - abs(self.latitude))))


@dataclass
class PressureSystem:
    """气压系统状态

    Args:
        central_pressure: 中心气压 (hPa)
        pressure_trend: 气压趋势 (上升/下降/稳定)
        system_type: 系统类型 (低气压/高气压/锋面)
    """
    central_pressure: float = 1013.0
    pressure_trend: str = "stable"
    system_type: Optional[str] = None

    def is_low_pressure(self) -> bool:
        return self.central_pressure < 1010

    def is_high_pressure(self) -> bool:
        return self.central_pressure > 1025

    @classmethod
    def from_trend(cls, pressure: float, prev_pressure: float):
        """从当前和上一时刻气压创建"""
        trend = "stable" if abs(pressure - prev_pressure) < 3 \
            else ("rising" if pressure > prev_pressure else "falling")
        return cls(central_pressure=pressure, pressure_trend=trend)


# ==================== 大气强迫修正器（v2 改进版） ====================

class AtmosphericForcingModifier:
    """大气强迫修正器

    根据外部参数调整天气状态转移概率，模拟真实大气响应。
    """

    ZONE_INFO = {
        "tropical": (23.5, -23.5),
        "subtropical": (40, 23.5),
        "temperate": (65, 40),
        "polar": (90, 65),
    }

    ELEVATION_TEMP_COEF = -0.0065  # °C/米

    @classmethod
    def get_zone(cls, latitude: float) -> str:
        """根据纬度返回气候带"""
        if abs(latitude) <= 23.5:
            return "tropical"
        elif abs(latitude) <= 40:
            return "subtropical"
        elif abs(latitude) <= 65:
            return "temperate"
        else:
            return "polar"

    @classmethod
    def apply_elevation_correction(cls, temp: float, elevation: float) -> float:
        """应用海拔高度温度修正，带极值钳制"""
        return max(-60.0, min(55.0, temp + (elevation * cls.ELEVATION_TEMP_COEF)))

    @classmethod
    def get_diurnal_modification(
        cls,
        latitude: float,
        hour: int,
        season: str,
        base_temp: float,
    ) -> float:
        """
        计算日变化温度的调制量（余弦曲线，更符合自然）

        夏季峰值提前（约 12 点）、振幅大（~12°C）
        冬季峰值延后（约 16 点）、振幅小（~6°C）

        Returns:
            日振幅调制后的绝对温度（已包含 base_temp）
        """
        peak_offset = {
            "summer": -2,
            "winter": +2,
            "spring": -1,
            "autumn": +1,
        }.get(season.lower(), 0)

        day_amplitude = {
            "summer": 12,
            "winter": 6,
            "spring": 8,
            "autumn": 7,
        }.get(season.lower(), 5)

        hour_from_peak = hour + peak_offset - 14

        if hour_from_peak == 0:
            return base_temp

        # 余弦曲线：0 点（14 时）为峰值
        shift = day_amplitude * math.cos(math.radians(hour_from_peak * 360 / 24))
        result = base_temp + shift
        return max(-60.0, min(55.0, result))

    def modify_transition_probability(
        self,
        zone: str,
        current_state: str,
        next_state: str,
    ) -> float:
        """
        根据外部大气强迫条件修改状态转移概率

        Args:
            zone: 气候带
            current_state: 当前天气状态
            next_state: 目标天气状态

        Returns:
            修正后的转移概率
        """
        base_prob = 0.5

        if zone == "tropical":
            if current_state == "CLEAR" and next_state in ("CLOUDY", "OVERCAST"):
                return max(base_prob, base_prob + 0.15)
        elif zone == "polar":
            if current_state != next_state:
                return max(0, base_prob - 0.1)

        return base_prob


# ==================== 大气稳定性（v2 改进版） ====================

def calculate_atmospheric_stability(
    temperature_surface: float,
    temperature_altitude: Optional[float] = None,
    current_pressure: float = 1013.0,
    dewpoint_surface: Optional[float] = None,
) -> Tuple[float, str]:
    """
    计算大气稳定性指数

    Args:
        temperature_surface: 地面温度 (°C)
        temperature_altitude: 高空温度（约 2000 米）(°C)
        current_pressure: 当前气压 (hPa)
        dewpoint_surface: 地面露点温度，用于计算湿度因子

    Returns:
        (稳定性指数, 描述文本)
        指数范围：-1 (极稳定/逆温) 到 +1 (极不稳定/强对流)
    """
    t_surf = max(-60.0, min(55.0, temperature_surface))

    if temperature_altitude is not None:
        t_alt = max(-60.0, min(55.0, temperature_altitude))
        lapse_rate = t_surf - t_alt
    else:
        lapse_rate = 0.0

    inversion = lapse_rate < 0

    humidity_factor = 0.0
    if dewpoint_surface is not None:
        dp = max(-60.0, min(55.0, dewpoint_surface))
        spread = t_surf - dp
        humidity_factor = max(0, (30 - spread) / 30)

    if inversion:
        stability = -0.7 + humidity_factor * 0.2
    elif lapse_rate > 10:
        stability = 0.6 + humidity_factor * 0.3
    elif lapse_rate < -5:
        stability = -0.5 - humidity_factor * 0.3
    else:
        stability = (lapse_rate / 20) + humidity_factor * 0.25

    stability = max(-1.0, min(1.0, stability))

    if stability > 0.5:
        desc = "不稳定（有利对流）"
    elif stability > 0.1:
        desc = "中性偏不稳定"
    elif stability < -0.5:
        desc = "极稳定（逆温层）"
    elif stability < -0.1:
        desc = "弱稳定"
    else:
        desc = "中性稳定"

    return round(stability, 2), desc


# ==================== 降水概率（v2 改进版） ====================

def calculate_precipitation_probability(
    sky_state: str,
    humidity: float,
    stability_index: float,
    pressure_trend: str = "neutral",
    temp: float = 20.0,
) -> float:
    """
    计算综合降水概率

    考虑：云量、湿度、大气稳定性、气压趋势、温度

    Args:
        sky_state: 天空状态 ("CLEAR" / "PARTLY_CLOUDY" / "CLOUDY" / "OVERCAST")
        humidity: 湿度因子 (0-1)
        stability_index: 大气稳定性指数 (-1 ~ 1, 正=不稳定)
        pressure_trend: 气压趋势 ("falling" / "rising" / "neutral")
        temp: 温度 (°C)，辅助判断

    Returns:
        降水概率 (0-1)
    """
    cloud_weights = {
        "CLEAR": 0.05,
        "PARTLY_CLOUDY": 0.2,
        "CLOUDY": 0.6,
        "OVERCAST": 1.0,
    }
    cloud_factor = cloud_weights.get(sky_state.upper(), 0.3)
    prob = cloud_factor * 0.4

    humidity_contribution = max(0, humidity - 0.4)
    prob += humidity_contribution * 0.3

    stability_contribution = max(0, stability_index)
    prob += stability_contribution * 0.25

    if pressure_trend == "falling":
        prob += 0.1
    elif pressure_trend == "rising":
        prob -= 0.05

    return min(1.0, max(0.0, prob))


# ==================== 降水强度计算 ====================

def compute_precipitation_intensity(rainfall_rate: float) -> str:
    """根据降雨速率计算降水强度描述"""
    if rainfall_rate <= 0:
        return "NONE"
    elif rainfall_rate < 1:
        return "LIGHT"
    elif rainfall_rate < 2:
        return "MODERATE"
    elif rainfall_rate < 5:
        return "HEAVY"
    else:
        return "EXTREME"


# ==================== 降水条件判定 ====================

@dataclass
class PrecipitationCondition:
    """降水条件计算

    Args:
        temperature: 温度 (°C)
        humidity: 相对湿度 (0-1)
        pressure_trend: 气压变化趋势
        stability_index: 大气稳定性指数 (负=稳定, 正=不稳定)
    """
    temperature: float
    humidity: float
    pressure_trend: str = "neutral"
    stability_index: float = 0.0

    def should_precipitate(self) -> bool:
        """判断是否满足降水条件"""
        if self.temperature > 25 and self.humidity > 0.7 and self.stability_index > 0.6:
            return True
        if self.pressure_trend == "falling" and self.humidity > 0.5:
            return True
        return False

    def get_precipitation_type(self) -> Optional[str]:
        """根据条件判断降水类型"""
        if not self.should_precipitate():
            return None
        if self.temperature < -3:
            return "snow"
        elif 0 < self.temperature < 5 and self.humidity > 0.8:
            return "sleet"
        else:
            return "rain"


# ==================== 温度-湿度耦合推导 ====================

def temp_to_sky(temp: float, humidity: float, latitude: float = 35):
    """简化版温度-湿度耦合推导天空状态"""
    temp = max(-60.0, min(55.0, temp))
    humidity = max(0.0, min(1.0, humidity))

    if temp > 28:
        sky = "CLEAR"
        cloud_cover = 0.1
    elif temp > 15:
        if humidity > 0.75:
            sky = "OVERCAST"
            cloud_cover = 0.9
        elif humidity > 0.6:
            sky = "CLOUDY"
            cloud_cover = 0.7
        else:
            sky = "PARTLY_CLOUDY"
            cloud_cover = 0.4
    elif temp > -5:
        sky = "CLOUDY"
        cloud_cover = 0.85 if humidity > 0.85 else 0.6
    elif temp < -20:
        sky = "OVERCAST" if humidity > 0.7 else "PARTLY_CLOUDY"
        cloud_cover = 0.9 if humidity > 0.7 else 0.3
    else:
        sky = "PARTLY_CLOUDY"
        cloud_cover = 0.5

    return sky, cloud_cover


# ==================== 太阳辐射相关 ====================

def clear_sky_radiation(temp: float) -> float:
    """计算晴朗天空辐射（简化斯蒂芬-玻尔兹曼定律）"""
    temp_kelvin = max(-273.15, temp) + 273.15
    sigma = 5.67e-8
    return (sigma * temp_kelvin ** 4) / 1000


def surface_radiation_emission(temp: float) -> float:
    """计算地表辐射发射（简化版，地表 emissivity ≈ 0.95）"""
    temp_kelvin = max(-273.15, temp) + 273.15
    sigma = 5.67e-8
    return sigma * (0.95 * temp_kelvin ** 4) / 1000


def compute_solar_radiation(
    height: float,
    latitude: float,
    solar_elevation: float,
    cloud_cover: float,
    clear_sky_temp: float,
) -> float:
    """计算太阳辐射（简化模型）"""
    atmospheric_factor = max(0.2, 1.0 - (height / 8)) * 0.5
    elevation_factor = max(0, math.sin(math.radians(solar_elevation)))
    clear_sky_rad = clear_sky_temp / 283.15 ** 4 * 1000 * 0.7
    return atmospheric_factor * elevation_factor * (1 - cloud_cover) * clear_sky_rad


def get_solar_elevation(latitude: float, hour: int, day_of_year: int) -> float:
    """计算太阳高度角（简化版）"""
    epsilon_deg = 23.44 * math.sin(math.radians(360 / 365 * (day_of_year - 81)))
    local_mean_time = hour - 12 + 120 / 15 / 15
    h = 15 * local_mean_time
    lat_rad = math.radians(latitude)
    epsilon_rad = math.radians(epsilon_deg)
    h_rad = math.radians(h)
    sin_alt = (
        math.sin(lat_rad) * math.sin(epsilon_rad)
        + math.cos(lat_rad) * math.cos(epsilon_rad) * math.cos(h_rad)
    )
    return max(-90, min(90, math.degrees(math.asin(sin_alt))))


# ==================== 气压相关 ====================

def get_pressure_trend(current: float, prev: Optional[float]) -> str:
    """从当前和前一时刻气压得到趋势"""
    if prev is None:
        return "neutral"
    diff = current - prev
    if abs(diff) < 1:
        return "neutral"
    elif diff > 0:
        return "rising"
    else:
        return "falling"


def update_pressure(current: float, prev: Optional[float], new_value: float):
    """更新气压并返回前一时刻值"""
    if prev is None:
        return new_value, current
    prev = current
    return new_value, prev


# ==================== 季节气候模式 ====================

SEASONAL_PATTERNS = {
    "summer": {
        "temp_range": (20, 38),
        "humidity_range": (0.3, 0.9),
        "pressure_range": (1005, 1025),
        "wind_speed_range": (0.5, 6),
    },
    "winter": {
        "temp_range": (-15, 8),
        "humidity_range": (0.3, 0.7),
        "pressure_range": (1010, 1035),
        "wind_speed_range": (1, 8),
    },
    "spring": {
        "temp_range": (5, 28),
        "humidity_range": (0.4, 0.8),
        "pressure_range": (1008, 1028),
        "wind_speed_range": (1, 7),
    },
    "autumn": {
        "temp_range": (3, 25),
        "humidity_range": (0.4, 0.75),
        "pressure_range": (1012, 1030),
        "wind_speed_range": (0.5, 5),
    },
}
