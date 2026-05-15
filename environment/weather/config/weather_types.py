
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:weather_state.py
@说明:天气状态枚举类
@时间:2026/03/09 10:07:22
@作者:Sherry
@版本:1.0
'''


from enum import Enum
from dataclasses import dataclass


# =========================
# 云量
# =========================
class SkyState(Enum):
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    OVERCAST = "overcast"


# =========================
# 降水类型
# =========================
class PrecipitationType(Enum):
    NONE = "none"
    RAIN = "rain"
    SNOW = "snow"
    SLEET = "sleet"
    HAIL = "hail"


# =========================
# 降水强度
# =========================
class PrecipitationIntensity(Enum):
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    EXTREME = "extreme"


# =========================
# 能见度
# =========================
class VisibilityState(Enum):
    CLEAR = "clear"
    FOG = "fog"
    DENSE_FOG = "dense_fog"
    HAZE = "haze"


# =========================
# 风力
# =========================
class WindLevel(Enum):
    CALM = "calm"
    BREEZE = "breeze"
    STRONG = "strong"
    GALE = "gale"
    STORM = "storm"


# =========================
# 极端天气
# =========================
class ExtremeWeather(Enum):
    NONE = "none"
    THUNDERSTORM = "thunderstorm"
    BLIZZARD = "blizzard"
    SANDSTORM = "sandstorm"
    TORNADO = "tornado"
    HURRICANE = "hurricane"


# =========================
# 天气状态（核心结构）
# =========================
@dataclass
class WeatherState:
    sky: SkyState = SkyState.CLEAR
    precipitation_type: PrecipitationType = PrecipitationType.NONE
    precipitation_intensity: PrecipitationIntensity = PrecipitationIntensity.NONE
    visibility: VisibilityState = VisibilityState.CLEAR
    wind: WindLevel = WindLevel.CALM
    extreme: ExtremeWeather = ExtremeWeather.NONE

    def __post_init__(self):
        """初始化后自动调用，确保状态一致性"""
        # 如果有极端天气，确保天空状态正确反映
        if self.extreme != ExtremeWeather.NONE:
            # 极端天气通常伴随特定天空状态
            extreme_sky_map = {
                ExtremeWeather.THUNDERSTORM: SkyState.OVERCAST,
                ExtremeWeather.BLIZZARD: SkyState.OVERCAST,
                ExtremeWeather.SANDSTORM: SkyState.CLOUDY,
                ExtremeWeather.TORNADO: SkyState.OVERCAST,
                ExtremeWeather.HURRICANE: SkyState.OVERCAST,
            }
            self.sky = extreme_sky_map.get(self.extreme, self.sky)

    @classmethod
    def from_physical_state(cls, temp: float, rainfall_rate: float, humidity: float 
                           , wind_speed: float, latitude: float, hour: int) -> 'WeatherState':
        """
        从连续物理量构建天气状态
        
        Args:
            temp: 温度 (°C)
            rainfall_rate: 降雨速率 (mm/h)
            humidity: 相对湿度 (%)
            wind_speed: 风速 (m/s)
            latitude: 纬度
            hour: 小时（0-23）
            
        Returns:
            WeatherState 实例
        """
        # 根据物理量推断离散状态
        
        # 1. 天空状态判断
        if rainfall_rate > 0 or humidity > 0.8:
            sky = SkyState.PARTLY_CLOUDY if humidity < 0.6 else SkyState.CLOUDY
        elif temp > 30 and humidity < 0.4:
            sky = SkyState.CLEAR
        else:
            # 使用温度范围判断（结合其他因素）
            base_sky = cls._get_sky_from_temp(temp, latitude)
            if rainfall_rate > 0:
                base_sky = SkyState.OVERCAST
            sky = base_sky
        
        # 2. 降水类型判断
        precip_type, precip_intensity = cls._infer_precipitation(
            rainfall_rate, humidity, temp, latitude, hour
        )
        
        # 3. 能见度判断
        visibility = VisibilityState.CLEAR
        if wind_speed > 5 or rainfall_rate > 5 or humidity > 0.9:
            visibility = cls._infer_visibility(rainfall_rate, humidity)
        
        # 4. 风力等级判断
        wind_level = WindLevel.CALM
        if wind_speed > 17.1:
            wind_level = WindLevel.STORM
        elif wind_speed > 11.2:
            wind_level = WindLevel.GALE
        elif wind_speed > 6.1:
            wind_level = WindLevel.STRONG
        elif wind_speed > 3.4:
            wind_level = WindLevel.BREEZE
        
        return cls(
            sky=sky,
            precipitation_type=precip_type,
            precipitation_intensity=precip_intensity,
            visibility=visibility,
            wind=wind_level,
            extreme=ExtremeWeather.NONE
        )

    @staticmethod
    def _get_sky_from_temp(temp: float, latitude: float) -> SkyState:
        """根据温度和纬度推断天空状态"""
        if temp > 25:
            # 高温 → 晴朗（假设无降水）
            return SkyState.CLEAR
        elif temp < 0:
            return SkyState.OVERCAST
        else:
            # 中性温度 → 部分多云
            return SkyState.PARTLY_CLOUDY

    @staticmethod
    def _infer_precipitation(rainfall_rate: float, humidity: float 
                             , temp: float, latitude: float, hour: int) -> tuple:
        """
        根据物理量推断降水类型和强度
        
        Args:
            rainfall_rate: 降雨速率
            humidity: 相对湿度
            temp: 温度
            latitude: 纬度
            hour: 小时
            
        Returns:
            (PrecipitationType, PrecipitationIntensity)
        """
        # 降水类型判断 - 基于温度和湿度
        if rainfall_rate <= 0:
            return PrecipitationType.NONE, PrecipitationIntensity.NONE
        
        # 温度-纬度组合判断降水相态
        effective_temp = temp - (latitude * 0.5)  # 纬度修正
        
        if humidity > 0.6 and effective_temp < -3:
            precip_type = PrecipitationType.SNOW
        elif humidity > 0.4 and effective_temp > 2:
            precip_type = PrecipitationType.RAIN
        else:
            # 边界情况
            precip_type = PrecipitationType.RAIN
        
        # 强度判断
        if rainfall_rate >= 50:
            intensity = PrecipitationIntensity.EXTREME
        elif rainfall_rate >= 25:
            intensity = PrecipitationIntensity.HEAVY
        elif rainfall_rate >= 10:
            intensity = PrecipitationIntensity.MODERATE
        else:
            intensity = PrecipitationIntensity.LIGHT
        
        return precip_type, intensity

    @staticmethod
    def _infer_visibility(rainfall_rate: float, humidity: float) -> VisibilityState:
        """推断能见度状态"""
        if rainfall_rate > 20 or humidity > 0.95:
            return VisibilityState.DENSE_FOG
        elif rainfall_rate > 10 or humidity > 0.85:
            return VisibilityState.FOG
        elif rainfall_rate > 5 or humidity > 0.7:
            return VisibilityState.HAZE
        return VisibilityState.CLEAR

    @classmethod
    def from_dict(cls, data: dict) -> 'WeatherState':
        """从字典构建"""
        return cls(
            sky=SkyState.from_value(data.get("sky", "clear")) if isinstance(data.get("sky"), str) else (data.get("sky") or SkyState.CLEAR),
            precipitation_type=PrecipitationType.from_value(data.get("precipitation_type", "none")) if isinstance(data.get("precipitation_type"), str) else (data.get("precipitation_type") or PrecipitationType.NONE),
            precipitation_intensity=PrecipitationIntensity.from_value(data.get("precipitation_intensity", "none")) if isinstance(data.get("precipitation_intensity"), str) else (data.get("precipitation_intensity") or PrecipitationIntensity.NONE),
            visibility=VisibilityState.from_value(data.get("visibility", "clear")) if isinstance(data.get("visibility"), str) else (data.get("visibility") or VisibilityState.CLEAR),
            wind=WindLevel.from_value(data.get("wind", "calm")) if isinstance(data.get("wind"), str) else (data.get("wind") or WindLevel.CALM),
            extreme=ExtremeWeather.from_value(data.get("extreme", "none")) if isinstance(data.get("extreme"), str) else (data.get("extreme") or ExtremeWeather.NONE)
        )