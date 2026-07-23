#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AtmospherePhysicsSystem - 大气物理计算系统

职责：
- 基于 ISA 标准大气模型计算气压和空气密度
- 提供海拔相关的大气参数查询
- 在 atmosphere 数据变化时自动重算派生值

原位于 AtmosphereComponent 中的物理计算逻辑已迁移至此。
"""

import math
from core.system import System
from core.world import World
from environment.atmosphere.components.atmosphere_component import AtmosphereComponent


# ── ISA 标准大气常数 ──
_ISA_SEA_LEVEL_PRESSURE = 1013.25
_ISA_SEA_LEVEL_TEMP = 288.15
_ISA_LAPSE_RATE = 0.0065
_ISA_TROPOPAUSE_ALT = 11000.0
_ISA_TROPOPAUSE_TEMP = 216.65
_ISA_GAS_CONSTANT = 287.05
_ISA_GRAVITY = 9.80665
_ISA_EXPONENT = _ISA_GRAVITY / (_ISA_GAS_CONSTANT * _ISA_LAPSE_RATE)


class AtmospherePhysicsSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """大气物理计算系统，负责 ISA 模型与派生参数计算。"""

    priority = 20  # 环境管线内

    # ═══════════════════════════════════════════════
    # ISA 标准大气模型
    # ═══════════════════════════════════════════════

    @staticmethod
    def isa_pressure(altitude: float) -> float:
        """
        国际标准大气（ISA）模型 — 计算指定海拔的气压（hPa）。
        """
        if altitude <= 0.0:
            return _ISA_SEA_LEVEL_PRESSURE

        if altitude <= _ISA_TROPOPAUSE_ALT:
            ratio = 1.0 - _ISA_LAPSE_RATE * altitude / _ISA_SEA_LEVEL_TEMP
            if ratio <= 0.0:
                return 0.0
            return _ISA_SEA_LEVEL_PRESSURE * (ratio ** _ISA_EXPONENT)
        else:
            p_tropopause = _ISA_SEA_LEVEL_PRESSURE * (
                (1.0 - _ISA_LAPSE_RATE * _ISA_TROPOPAUSE_ALT / _ISA_SEA_LEVEL_TEMP)
                ** _ISA_EXPONENT
            )
            h_above = altitude - _ISA_TROPOPAUSE_ALT
            return p_tropopause * math.exp(
                -_ISA_GRAVITY * h_above / (_ISA_GAS_CONSTANT * _ISA_TROPOPAUSE_TEMP)
            )

    @staticmethod
    def isa_temperature(altitude: float) -> float:
        """
        ISA 标准温度（K）在指定海拔的值。
        """
        if altitude <= _ISA_TROPOPAUSE_ALT:
            return _ISA_SEA_LEVEL_TEMP - _ISA_LAPSE_RATE * max(altitude, 0.0)
        else:
            return _ISA_TROPOPAUSE_TEMP

    # ═══════════════════════════════════════════════
    # 空气密度计算
    # ═══════════════════════════════════════════════

    @staticmethod
    def update_air_density(atm: AtmosphereComponent) -> float:
        """
        根据当前 pressure 和 temperature 计算空气密度（kg/m³）。
        返回值同时写入 atm.air_density。
        """
        t_kelvin = atm.temperature + 273.15
        if t_kelvin < 80.0:
            t_kelvin = 80.0
        atm.air_density = atm.pressure * 100.0 / (_ISA_GAS_CONSTANT * t_kelvin)
        return atm.air_density

    # ═══════════════════════════════════════════════
    # 海拔相关辅助方法
    # ═══════════════════════════════════════════════

    @staticmethod
    def recalculate_from_altitude(atm: AtmosphereComponent):
        """
        根据当前 altitude 重算 pressure 和 air_density。
        当 altitude 被外部修改（如地形调整）后调用。
        """
        atm.pressure = AtmospherePhysicsSystem.isa_pressure(atm.altitude)
        AtmospherePhysicsSystem.update_air_density(atm)

    @staticmethod
    def get_oxygen_partial_pressure(atm: AtmosphereComponent) -> float:
        """计算氧气分压（hPa）"""
        return atm.pressure * atm.oxygen_ratio

    @staticmethod
    def get_effective_oxygen_ratio(atm: AtmosphereComponent) -> float:
        """
        获取相对于海平面的有效氧气比例。
        在 3000m 海拔时有效氧约为海平面的 70%。
        """
        return (atm.pressure / _ISA_SEA_LEVEL_PRESSURE) * atm.oxygen_ratio

    @staticmethod
    def get_temperature_altitude_effect(atm: AtmosphereComponent) -> float:
        """
        获取温度和海拔对大气的综合影响程度。
        Returns: 温度偏离标准值程度 + 海拔偏离程度（归一化）
        """
        temp_deviation = abs(atm.temperature - 15) / 100.0
        altitude_deviation = atm.altitude / 8883.0
        return temp_deviation + altitude_deviation

    # ═══════════════════════════════════════════════
    # System update
    # ═══════════════════════════════════════════════

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)
        atm = world.get_world_component(AtmosphereComponent)
        if atm is None:
            return
        # 若 air_density 未初始化或 pressure/temperature 已变化，自动同步
        # 注：实际变化检测由各子系统（ThermodynamicsSystem 等）负责写入后触发
        if getattr(atm, 'air_density', None) is None:
            self.update_air_density(atm)