#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大气组件（拟真扩展版）

维护大气的物理变量，增加温度、海拔等核心参数以支持更真实的物理模拟。
"""

from dataclasses import dataclass, field, fields as dc_fields
from core.component import Component


@dataclass
class AtmosphereComponent(Component):
    """
    大气状态组件（扩展版）
    
    WeatherComponent 只保存"天气结果"
    AtmosphereComponent 保存"物理状态"
    
    扩展内容：
    - 增加 temperature 温度（°C），影响空气密度、水汽饱和度
    - 增加 altitude 海拔高度（m），影响气压递减
    - 保留原有气体参数、湿度系统、对流系统、云层、风场等
    """

    # ===============================
    # 基础物理参数（新增）
    # ===============================

    temperature: float = 20.0        # 温度 °C（核心物理量，影响密度/湿度）
    altitude: float = 0.0            # 海拔高度（m），用于气压递减计算
    
    pressure: float = 1013.25        # 气压 hPa（与海拔、温度关联）
    air_density: float = field(init=False)  # 空气密度 kg/m³，自动计算

    oxygen_ratio: float = 0.209      # 氧气比例
    co2_ratio: float = 0.00042       # 二氧化碳比例

    aerosol: float = 0.0             # 气溶胶

    # ===============================
    # 湿度系统
    # ===============================

    humidity: float = 0.5            # 相对湿度（%）
    water_vapor: float = 0.01        # 水汽含量 kg/kg

    # ===============================
    # 对流系统
    # ===============================

    convection_strength: float = 0.0 # 对流强度（基于温度逆增计算）
    turbulence: float = 0.0          # 湍流

    # ===============================
    # 云层
    # ===============================

    cloud_cover: float = 0.0         # 云量 0-1
    cloud_density: float = 0.0       # 云厚度

    # ===============================
    # 风场
    # ===============================

    wind_speed: float = 0.0          # m/s
    wind_direction: float = 0.0      # 0-360

    def __post_init__(self):
        """
        初始化后自动计算空气密度
        
        使用理想气体状态方程：ρ = P / (R · T)
        同时考虑海拔对气压的影响
        """
        self._update_air_density()

    def _update_air_density(self):
        """
        计算空气密度
        
        考虑三个因素：
        1. 温度（理想气体）
        2. 海拔（国际大气模型，海平面气压随高度递减）
        3. 当前气压（允许用户直接设置，用于模拟气压变化
        """
        # 标准气温递减率 (°C/m)，仅适用于对流层
        LapseRate = 6.5 / 100  # °C/m
        
        # 计算该海拔的理论温度（基于地面温度）
        alt_temp = self.temperature - (self.altitude * LapseRate) * 100
        
        # T in Kelvin
        T_kelvin = alt_temp + 273.15 if alt_temp > -194.4 else 80.15  # -194.4°C为绝对零度附近
        
        # R for dry air = 287.05 J/(kg·K)
        R = 287.05
        
        # 根据理想气体定律计算密度
        # P in hPa -> Pa: multiply by 100
        # Result in kg/m³
        self.air_density = self.pressure * 100 / (R * T_kelvin)

    def to_dict(self):
        """
        序列化成字典（仅包含非 None 属性的字段）
        """
        result = {}
        for f in dc_fields(self):
            value = getattr(self, f.name)
            if value is not None:
                result[f.name] = value
        return result

    @staticmethod
    def from_dict(data: dict):
        """
        从字典反序列化

        Args:
            data: 要反序列化的数据字典。仅存在字段会被更新，其他字段保留默认值。

        Returns:
            新的 AtmosphereComponent 实例
        """
        attrs = {f.name: getattr(data, f.name) for f in dc_fields(AtmosphereComponent)}
        return AtmosphereComponent(**attrs)

    def get_state(self):
        """
        获取当前状态字典（仅包含已设置的属性）

        与 to_dict() 相同，保留语义一致性。
        """
        return self.to_dict()

    def set_state_from_dict(self, data: dict):
        """
        从字典设置状态（增量更新）

        Args:
            data: 要应用的状态字典。仅存在的字段会被更新，其他字段保留原值。
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_state_from_dict_maybe(self, data: dict):
        """
        从字典设置状态（增量更新）,允许传入None和缺失参数

        Args:
            data: 要应用的状态字典。仅存在的字段会被更新，其他字段保留原值。
        """
        for key, value in data.items():
            if key in self.__dataclass_fields__:
                setattr(self, key, value)
        # 确保在从dict设置后重新计算空气密度
        self._update_air_density()

    def get_temperature_altitude_effect(self):
        """
        获取温度和海拔对大气的综合影响程度
        
        Returns:
            float: 温度偏离标准值程度 + 海拔偏离程度（归一化）
        """
        # 温度偏离（相对于标准大气温度，地面为15°C）
        temp_deviation = abs(self.temperature - 15) / 100 * 1
        
        # 海拔偏离
        altitude_deviation = self.altitude / 8883  # 8883m是国际标准大气模型中气压减半的高度
        
        return temp_deviation + altitude_deviation
