#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大气组件（拟真扩展版）

维护大气的物理变量，增加温度、海拔等核心参数以支持更真实的物理模拟。
基于国际标准大气（ISA）模型计算气压和空气密度随海拔的变化。
"""

import math

from dataclasses import dataclass, field, fields as dc_fields
from core.component import Component


# ── ISA 标准大气常数 ──
_ISA_SEA_LEVEL_PRESSURE = 1013.25       # hPa
_ISA_SEA_LEVEL_TEMP = 288.15           # K (= 15°C)
_ISA_LAPSE_RATE = 0.0065               # K/m (对流层标准气温递减率)
_ISA_TROPOPAUSE_ALT = 11000.0          # m
_ISA_TROPOPAUSE_TEMP = 216.65          # K (= -56.5°C)
_ISA_GAS_CONSTANT = 287.05             # J/(kg·K) 干空气气体常数
_ISA_GRAVITY = 9.80665                 # m/s²
_ISA_EXPONENT = _ISA_GRAVITY / (_ISA_GAS_CONSTANT * _ISA_LAPSE_RATE)  # ≈ 5.2561


@dataclass
class AtmosphereComponent(Component):
    """
    大气状态组件（扩展版）

    核心设计：
    - altitude（海拔）为自变量 → 自动推导 pressure（气压）和 air_density（空气密度）
    - 用户可显式设置 pressure 覆盖 ISA 模型
    - oxygen_ratio / co2_ratio 支持高海拔低氧场景的自定义
    """

    # ===
    # 基础物理参数
    # ===

    temperature: float = 20.0        # 温度 °C（核心物理量，影响密度/湿度）
    altitude: float = 0.0            # 海拔高度（m），用于气压和密度计算

    pressure: float = _ISA_SEA_LEVEL_PRESSURE  # 气压 hPa（init 时由 altitude 覆盖）
    air_density: float = field(init=False)      # 空气密度 kg/m³，自动计算

    oxygen_ratio: float = 0.209      # 氧气比例（可针对高海拔低氧场景调整）
    co2_ratio: float = 0.00042       # 二氧化碳比例

    aerosol: float = 0.0             # 气溶胶

    # ===
    # 湿度系统
    # ===

    humidity: float = 0.5            # 相对湿度（%）
    water_vapor: float = 0.01        # 水汽含量 kg/kg

    # ===
    # 对流系统
    # ===

    convection_strength: float = 0.0 # 对流强度（基于温度逆增计算）
    turbulence: float = 0.0          # 湍流

    # ===
    # 云层
    # ===

    cloud_cover: float = 0.0         # 云量 0-1
    cloud_density: float = 0.0       # 云厚度

    # ===
    # 风场
    # ===

    wind_speed: float = 0.0          # m/s
    wind_direction: float = 0.0      # 0-360

    # ── 私有标记：用户是否显式设置了 pressure ──
    _pressure_explicit: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self):
        """
        初始化后自动计算气压与空气密度。

        逻辑：
        - altitude 为自变量，pressure 由 ISA 模型自动推导
        - 用户显式传入 pressure 时，以用户值为准（不覆盖）
        - 始终根据 pressure + temperature 计算 air_density

        ⚠️ 如果创建后修改 altitude，请调用 recalculate_from_altitude() 同步。
        """
        if self.altitude > 0:
            # 只有在 pressure 仍为默认值 1013.25 时才自动计算
            if abs(self.pressure - _ISA_SEA_LEVEL_PRESSURE) < 0.01:
                self.pressure = self._isa_pressure(self.altitude)
        self._update_air_density()

    # ═══════════════════════════════════════════════
    # ISA 标准大气模型
    # ═══════════════════════════════════════════════

    @staticmethod
    def _isa_pressure(altitude: float) -> float:
        """
        国际标准大气（ISA）模型 — 计算指定海拔的气压（hPa）。

        对流层 (0 ~ 11000m):  T = T0 - L*h,  P = P0 * (T/T0)^(g/RL)
        平流层 (> 11000m):    T = 216.65 K,   P = P11 * exp(-g*(h-11000)/(R*T11))

        Args:
            altitude: 海拔高度（m）

        Returns:
            气压（hPa）
        """
        if altitude <= 0.0:
            return _ISA_SEA_LEVEL_PRESSURE

        if altitude <= _ISA_TROPOPAUSE_ALT:
            # 对流层
            ratio = 1.0 - _ISA_LAPSE_RATE * altitude / _ISA_SEA_LEVEL_TEMP
            if ratio <= 0.0:
                return 0.0
            return _ISA_SEA_LEVEL_PRESSURE * (ratio ** _ISA_EXPONENT)
        else:
            # 平流层（温度恒定为 216.65K）
            p_tropopause = _ISA_SEA_LEVEL_PRESSURE * (
                (1.0 - _ISA_LAPSE_RATE * _ISA_TROPOPAUSE_ALT / _ISA_SEA_LEVEL_TEMP)
                ** _ISA_EXPONENT
            )
            h_above = altitude - _ISA_TROPOPAUSE_ALT
            return p_tropopause * math.exp(
                -_ISA_GRAVITY * h_above / (_ISA_GAS_CONSTANT * _ISA_TROPOPAUSE_TEMP)
            )

    @staticmethod
    def _isa_temperature(altitude: float) -> float:
        """
        ISA 标准温度（K）在指定海拔的值。

        对流层: T = 288.15 - 0.0065 * h  (K)
        平流层: T = 216.65 K
        """
        if altitude <= _ISA_TROPOPAUSE_ALT:
            return _ISA_SEA_LEVEL_TEMP - _ISA_LAPSE_RATE * max(altitude, 0.0)
        else:
            return _ISA_TROPOPAUSE_TEMP

    # ═══════════════════════════════════════════════
    # 空气密度计算
    # ═══════════════════════════════════════════════

    def _update_air_density(self):
        """
        计算空气密度。

        使用理想气体状态方程：ρ = P / (R · T)
        - P 以 hPa 传入 → 转换为 Pa (*100)
        - T 以 °C 传入 → 转换为 K (+273.15)
        - R = 287.05 J/(kg·K) 干空气气体常数
        """
        t_kelvin = self.temperature + 273.15
        # 保护：防止极低温导致密度异常
        if t_kelvin < 80.0:
            t_kelvin = 80.0

        self.air_density = self.pressure * 100.0 / (_ISA_GAS_CONSTANT * t_kelvin)

    # ═══════════════════════════════════════════════
    # 海拔相关辅助方法
    # ═══════════════════════════════════════════════

    def recalculate_from_altitude(self):
        """
        根据当前 altitude 重算 pressure 和 air_density。

        当 altitude 被外部修改（如地形调整）后调用此方法。
        """
        self.pressure = self._isa_pressure(self.altitude)
        self._update_air_density()

    def get_oxygen_partial_pressure(self) -> float:
        """
        计算氧气分压（hPa）。

        高海拔时气压下降，氧气分压也下降，模拟低氧效应。
        """
        return self.pressure * self.oxygen_ratio

    def get_effective_oxygen_ratio(self) -> float:
        """
        获取相对于海平面的有效氧气比例。

        在 3000m 海拔时有效氧约为海平面的 70%。
        用于生物代谢 / 呼吸系统的输入。
        """
        sea_level_p = _ISA_SEA_LEVEL_PRESSURE
        return (self.pressure / sea_level_p) * self.oxygen_ratio

    # ═══════════════════════════════════════════════
    # 序列化
    # ═══════════════════════════════════════════════

    def to_dict(self):
        """序列化成字典（仅包含非 None 属性的字段）"""
        result = {}
        for f in dc_fields(self):
            if f.name.startswith('_'):
                continue
            value = getattr(self, f.name)
            if value is not None:
                result[f.name] = value
        return result

    @staticmethod
    def from_dict(data: dict):
        """从字典反序列化"""
        # 只取类中定义的字段
        field_names = {f.name for f in dc_fields(AtmosphereComponent)
                       if not f.name.startswith('_')}
        attrs = {k: v for k, v in data.items() if k in field_names}
        return AtmosphereComponent(**attrs)

    def get_state(self):
        """获取当前状态字典"""
        return self.to_dict()

    def set_state_from_dict(self, data: dict):
        """从字典设置状态（增量更新）"""
        for key, value in data.items():
            if hasattr(self, key) and not key.startswith('_'):
                setattr(self, key, value)

    def set_state_from_dict_maybe(self, data: dict):
        """从字典设置状态，允许 None 和缺失参数"""
        for key, value in data.items():
            if key in self.__dataclass_fields__:
                setattr(self, key, value)
        # 重算空气密度
        self._update_air_density()

    def get_temperature_altitude_effect(self):
        """
        获取温度和海拔对大气的综合影响程度

        Returns:
            float: 温度偏离标准值程度 + 海拔偏离程度（归一化）
        """
        temp_deviation = abs(self.temperature - 15) / 100.0
        altitude_deviation = self.altitude / 8883.0  # 气压减半高度 ≈ 8883m
        return temp_deviation + altitude_deviation



