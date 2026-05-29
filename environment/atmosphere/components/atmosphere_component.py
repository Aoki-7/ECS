#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大气组件（纯数据）

维护大气的物理变量，增加温度、海拔等核心参数以支持更真实的物理模拟。
所有 ISA 模型计算与派生逻辑已迁移至 AtmospherePhysicsSystem。
"""

from dataclasses import dataclass, field, fields as dc_fields
from core.component import Component


@dataclass(slots=True)
class AtmosphereComponent(Component):
    """
    大气状态组件 — 纯数据容器

    核心设计：
    - altitude（海拔）为自变量 → 由 AtmospherePhysicsSystem 推导 pressure / air_density
    - oxygen_ratio / co2_ratio 支持高海拔低氧场景的自定义
    """

    # === 基础物理参数 ===
    temperature: float = 20.0        # 温度 °C
    altitude: float = 0.0            # 海拔高度 m
    pressure: float = 1013.25        # 气压 hPa
    air_density: float = 1.225       # 空气密度 kg/m³（海平面默认值）

    oxygen_ratio: float = 0.209      # 氧气比例
    co2_ratio: float = 0.00042       # 二氧化碳比例
    aerosol: float = 0.0             # 气溶胶

    # === 湿度系统 ===
    humidity: float = 0.5            # 相对湿度 %
    water_vapor: float = 0.01        # 水汽含量 kg/kg

    # === 对流系统 ===
    convection_strength: float = 0.0 # 对流强度
    turbulence: float = 0.0          # 湍流

    # === 云层 ===
    cloud_cover: float = 0.0         # 云量 0-1
    cloud_density: float = 0.0       # 云厚度

    # === 风场 ===
    wind_speed: float = 0.0          # m/s
    wind_direction: float = 0.0      # 0-360

    # ── 私有标记：用户是否显式设置了 pressure ──
    _pressure_explicit: bool = field(default=False, repr=False, compare=False)

    # ═══════════════════════════════════════════════
    # 序列化（数据转换，保留在组件内）
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
