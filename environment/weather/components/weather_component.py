#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
天气组件（环境系统核心组件）[扩展版]

该组件仅用于**存储天气状态数据**，不包含任何演化逻辑。
所有状态更新、马尔可夫转移、噪声注入等，应在 WeatherSystem 中完成。

---------------------------------------
【设计原则】
---------------------------------------

1. 多维正交状态（核心）
   天气由多个"独立维度"组成，而不是单一枚举：
   - 天空（云量）
   - 降水类型
   - 降水强度
   - 能见度
   - 风力

2. 物理量 vs 状态分离
   - 状态（Enum）：用于离散模拟/状态机
   - 物理量（float）：用于生态系统输入

3. 组件无逻辑
   - 不做状态转移
   - 不做概率计算
   - 不做噪声生成

4. 时间控制外置
   各状态持续时间仅作为"计时器"，
   是否触发变化由 system 决定。

---------------------------------------
【新增功能】
- 从 AtmosphereComponent 获取温度以自动更新饱和湿度
- 支持相对湿度阈值预警
"""

from typing import Tuple
import math

from dataclasses import dataclass, field
from core.component import Component

from environment.weather.config.weather_types import (
    SkyState,
    PrecipitationType,
    PrecipitationIntensity,
    VisibilityState,
    WindLevel,
    ExtremeWeather,
)


@dataclass
class WeatherComponent(Component):
    """天气状态组件
    
    存储当前天气的多维正交状态和连续物理量。
    
    【示例】
    >>> wc = WeatherComponent()
    >>> wc.sky = SkyState.CLOUDY
    >>> wc.temperature = 25.0
    """
    
    # ================================
    # 🌡 连续物理量（供生态系统使用）
    #    所有物理量由对应 System 维护更新，Component 只存储
    # ================================
    
    temperature: float = 20.0            # 温度 (°C) - 通常从 AtmosphereComponent 获取
    rainfall: float = 0.0                # 降雨速率 (mm/h)
    sunlight: float = 1.0                # 光照强度 (0~1) - 由 CloudSystem 根据云量与太阳角度计算
    
    # ================================
    # 🌥 云量演化（核心物理量）
    #    由 CloudSystem 维护，WeatherSystem 据此推导 sky 状态
    # ================================
    
    total_cloud_cover: float = 0.0       # 总云量 (0~1) - 由 CloudSystem 维护
    cloud_depth: float = 0.0             # 云层平均厚度 (km) - 用于遮挡计算
    vertical_profile: list[tuple] = field(default_factory=list)  # 高度-云量剖面 [(z1, cover1), ...]

    # ================================
    # 🌥 天空状态（视觉描述，与总云量映射）
    # ================================
    
    sky: SkyState = SkyState.CLEAR
    
    # ================================
    # 🌧 降水状态（多维正交）
    # ================================
    
    precipitation_type: PrecipitationType = PrecipitationType.NONE
    precipitation_intensity: PrecipitationIntensity = PrecipitationIntensity.NONE
    
    # ================================
    # 👁 能见度
    # ================================
    
    visibility: VisibilityState = VisibilityState.CLEAR
    
    # ================================
    # 💨 风力
    # ================================
    
    wind: WindLevel = WindLevel.CALM
    
    # ================================
    # ⛈ 极端天气标记
    # ================================
    
    extreme: ExtremeWeather = ExtremeWeather.NONE
    
    # ================================
    # ⏳ 状态持续时间（由 system 消耗）
    # ================================
    
    sky_remaining_hours: float = 6.0
    precipitation_type_remaining_hours: float = 3.0
    precipitation_intensity_remaining_hours: float = 2.0
    visibility_remaining_hours: float = 4.0
    wind_remaining_hours: float = 5.0
    extreme_remaining_hours: float = 10.0

    def to_dict(self) -> dict:
        """转换为字典（用于序列化/调试）"""
        return {
            "temperature": self.temperature,
            "rainfall": self.rainfall,
            "sunlight": self.sunlight,
            "sky": str(self.sky.value),
            "precipitation_type": str(self.precipitation_type.value),
            "precipitation_intensity": str(self.precipitation_intensity.value),
            "visibility": str(self.visibility.value),
            "wind": str(self.wind.value),
            "extreme": str(self.extreme.value),
            "sky_remaining_hours": self.sky_remaining_hours,
            "precipitation_type_remaining_hours": self.precipitation_type_remaining_hours,
            "precipitation_intensity_remaining_hours": self.precipitation_intensity_remaining_hours,
            "visibility_remaining_hours": self.visibility_remaining_hours,
            "wind_remaining_hours": self.wind_remaining_hours,
            "extreme_remaining_hours": self.extreme_remaining_hours,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WeatherComponent':
        """从字典重建（恢复状态）"""
        wc = cls()
        wc.temperature = data.get("temperature", wc.temperature)
        wc.rainfall = data.get("rainfall", wc.rainfall)
        wc.sunlight = data.get("sunlight", wc.sunlight)
        wc.sky = SkyState(data.get("sky", "CLEAR"))
        wc.precipitation_type = PrecipitationType(data.get("precipitation_type", "NONE"))
        wc.precipitation_intensity = PrecipitationIntensity(data.get("precipitation_intensity", "NONE"))
        wc.visibility = VisibilityState(data.get("visibility", "CLEAR"))
        wc.wind = WindLevel(data.get("wind", "CALM"))
        wc.extreme = ExtremeWeather(data.get("extreme", "NONE"))
        wc.sky_remaining_hours = data.get("sky_remaining_hours", wc.sky_remaining_hours)
        wc.precipitation_type_remaining_hours = data.get("precipitation_type_remaining_hours", wc.precipitation_type_remaining_hours)
        wc.precipitation_intensity_remaining_hours = data.get("precipitation_intensity_remaining_hours", wc.precipitation_intensity_remaining_hours)
        wc.visibility_remaining_hours = data.get("visibility_remaining_hours", wc.visibility_remaining_hours)
        wc.wind_remaining_hours = data.get("wind_remaining_hours", wc.wind_remaining_hours)
        wc.extreme_remaining_hours = data.get("extreme_remaining_hours", wc.extreme_remaining_hours)
        return wc


def saturated_vapor_pressure(temp_celsius: float) -> Tuple[float, float]:
    """
    计算饱和水汽压（Magnus公式）
    
    Args:
        temp_celsius: 温度 (°C), 建议范围 -100°C ~ 150°C
    
    Returns:
        (e_s, se_slope): 
            e_s - 饱和水汽压 [hPa]
            se_slope - 对温度的变化率 (近似) [hPa/°C]
    
    【公式说明】
    使用标准Magnus公式（Bolton, 1980简化版）：
        e_s = 6.112 * exp(17.27 * T / (T + 237.3)) [hPa]
    其中 T 为摄氏度。
    
    【注意】T 的单位必须是°C，不能使用开尔文。
    """
    if temp_celsius < -100 or temp_celsius > 150:
        raise ValueError(f"温度超出物理范围: {temp_celsius}°C")
    
    # Magnus公式（Bolton, 1980简化版）
    A = 6.112      # Pa (标准大气压下的饱和水汽压参考值)
    B = 17.27      # Magnus公式系数
    C = 237.3      # Magnus公式系数
    
    # 计算饱和水汽压 [hPa]
    e_s_hpa = A * (C + 237.3) / (C + temp_celsius)
    
    # 简化：直接用标准形式
    e_s = 6.112 * math.exp(B * temp_celsius / (temp_celsius + C))
    
    return e_s, B

