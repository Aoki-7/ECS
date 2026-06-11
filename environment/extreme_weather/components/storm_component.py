#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风暴组件

v3.5 新增 — P2

职责：
    - 存储风暴物理参数
    - 支持雷暴、龙卷风、飓风等

设计原则：
    - 纯物理量驱动：气压梯度、温度差、湿度
    - 无硬编码风暴行为，由大气条件自发形成
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.component import Component


@dataclass
class StormComponent(Component):
    """
    风暴组件

    物理参数：
    - 气压梯度 → 风速
    - 温度差 → 对流强度
    - 湿度 → 降水潜力
    - 科里奥利力 → 旋转（纬度相关）

    Attributes:
        storm_type: 风暴类型（thunderstorm/tornado/hurricane）
        intensity: 强度 (0-1，由物理条件计算)
        central_pressure: 中心气压 (hPa)
        pressure_gradient: 气压梯度 (hPa/km)
        max_wind_speed: 最大风速 (m/s)
        diameter: 风暴直径 (km)
        temperature_gradient: 温度梯度 (°C/km)
        humidity: 相对湿度 (0-1)
        latitude: 纬度 (度，影响科里奥利力)
        lifetime: 已存在时间 (小时)
        max_lifetime: 最大寿命 (小时，由能量供应决定)
    """

    storm_type: str = "thunderstorm"
    intensity: float = 0.0
    central_pressure: float = 1013.0
    pressure_gradient: float = 0.0
    max_wind_speed: float = 0.0
    diameter: float = 1.0
    temperature_gradient: float = 0.0
    humidity: float = 0.0
    latitude: float = 30.0
    lifetime: float = 0.0
    max_lifetime: float = 1.0

    def to_dict(self) -> dict:
        return {
            "storm_type": self.storm_type,
            "intensity": self.intensity,
            "central_pressure": self.central_pressure,
            "pressure_gradient": self.pressure_gradient,
            "max_wind_speed": self.max_wind_speed,
            "diameter": self.diameter,
            "temperature_gradient": self.temperature_gradient,
            "humidity": self.humidity,
            "latitude": self.latitude,
            "lifetime": self.lifetime,
            "max_lifetime": self.max_lifetime,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StormComponent":
        return cls(
            storm_type=data.get("storm_type", "thunderstorm"),
            intensity=data.get("intensity", 0.0),
            central_pressure=data.get("central_pressure", 1013.0),
            pressure_gradient=data.get("pressure_gradient", 0.0),
            max_wind_speed=data.get("max_wind_speed", 0.0),
            diameter=data.get("diameter", 1.0),
            temperature_gradient=data.get("temperature_gradient", 0.0),
            humidity=data.get("humidity", 0.0),
            latitude=data.get("latitude", 30.0),
            lifetime=data.get("lifetime", 0.0),
            max_lifetime=data.get("max_lifetime", 1.0),
        )

    @property
    def coriolis_parameter(self) -> float:
        """
        科里奥利参数 f = 2Ω·sin(φ)
        Ω = 7.292e-5 rad/s（地球自转角速度）
        φ = 纬度
        """
        omega = 7.292e-5
        # sin 近似（小角度）
        lat_rad = self.latitude * 0.0174533
        sin_lat = self._sin(lat_rad)
        return 2 * omega * sin_lat

    @property
    def wind_speed_from_pressure(self) -> float:
        """
        由气压梯度计算风速（地转风近似）
        Vg = (1/ρf) * (ΔP/Δn)
        ρ = 空气密度 ≈ 1.225 kg/m³
        """
        rho = 1.225
        f = abs(self.coriolis_parameter)
        
        if f < 1e-10:
            return 0.0
        
        # 气压梯度转换为 Pa/m
        gradient_pa_m = self.pressure_gradient * 100 / 1000  # hPa/km → Pa/m
        
        return gradient_pa_m / (rho * f)

    def _sin(self, theta: float) -> float:
        """简化的正弦计算"""
        # 归一化到 -π~π
        theta = theta % 6.283185307179586
        if theta > 3.141592653589793:
            theta = 6.283185307179586 - theta
            sign = -1
        else:
            sign = 1
        
        theta2 = theta * theta
        result = theta - theta * theta2 / 6 + theta * theta2 * theta2 / 120
        return sign * result

    def update_intensity(self) -> None:
        """
        根据物理条件更新强度
        强度由多个物理因素共同决定，无硬编码阈值
        """
        # 气压梯度贡献
        pressure_factor = min(1.0, self.pressure_gradient / 50.0)
        
        # 温度梯度贡献（对流）
        temp_factor = min(1.0, abs(self.temperature_gradient) / 10.0)
        
        # 湿度贡献（能量来源）
        humidity_factor = self.humidity
        
        # 综合强度（加权平均）
        self.intensity = (pressure_factor * 0.4 + temp_factor * 0.3 + humidity_factor * 0.3)
        
        # 更新最大风速
        self.max_wind_speed = self.wind_speed_from_pressure * self.intensity
