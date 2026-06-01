#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
热力学系统 [v2.0] — 基于 PhysicalWeather 计算大气热力学参数

【物理原理】
1. 空气密度 — 理想气体状态方程：ρ = P / (R·T)
2. 水汽饱和蒸气压 — Magnus 公式
3. 相对湿度同步 — 从 PhysicalWeatherComponent 读取并转换
4. 水汽含量 — 基于绝对湿度与温度计算

【职责边界】
- ✅ 负责：从 PhysicalWeatherComponent 同步温度/湿度到 AtmosphereComponent
- ✅ 负责：计算饱和水汽压、空气密度、水汽含量
- ❌ 不再负责：气压计算（由 PressureSystem 处理）
- ❌ 不再负责：云量计算（由 CloudSystem 处理）

【数据流】
PhysicalWeatherComponent (temperature, relative_humidity, absolute_humidity)
    → ThermodynamicsSystem
    → AtmosphereComponent (temperature, humidity, air_density, water_vapor)
"""

import math

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)


class ThermodynamicsSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    热力学系统

    将 PhysicalWeatherComponent 的连续物理量转换为
    AtmosphereComponent 的热力学参数。
    """

    # 干空气气体常数
    R_DRY_AIR = 287.05  # J/(kg·K)

    # Magnus formula coefficients for liquid water
    MAGNUS_A = 17.625
    MAGNUS_B = 243.04

    @staticmethod
    def saturated_vapor_pressure(temp_celsius: float) -> float:
        """
        计算饱和水汽压（Magnus-Tetens 公式，hPa）

        Args:
            temp_celsius: 温度 (°C)

        Returns:
            饱和水汽压 [hPa]
        """
        if temp_celsius < -40 or temp_celsius > 50:
            return max(1.0, min(100.0, 6.112 * math.exp((17.67 * temp_celsius) / (temp_celsius + 243.5))))

        A = ThermodynamicsSystem.MAGNUS_A
        B = ThermodynamicsSystem.MAGNUS_B
        return 6.1094 * math.exp((A * temp_celsius) / (B + temp_celsius))

    @staticmethod
    def actual_vapor_pressure(temp_celsius: float, relative_humidity: float) -> float:
        """
        计算实际水汽压（hPa）

        Args:
            temp_celsius: 温度 (°C)
            relative_humidity: 相对湿度 [0~1]

        Returns:
            实际水汽压 [hPa]
        """
        sat = ThermodynamicsSystem.saturated_vapor_pressure(temp_celsius)
        return sat * relative_humidity

    @staticmethod
    def absolute_humidity_from_vapor_pressure(e: float, temp_celsius: float) -> float:
        """
        将实际水汽压转换为绝对湿度（g/m³）

        公式：AH = 216.7 * e / (T + 273.15)
        - e: 实际水汽压 [hPa]
        - T: 温度 [°C]
        """
        t_kelvin = temp_celsius + 273.15
        if t_kelvin <= 0:
            return 0.0
        return 216.7 * e / t_kelvin

    def update(self, world: World, delta_hours: float):
        """
        热力学系统更新

        从 PhysicalWeatherComponent 读取物理量，
        计算热力学参数并同步到 AtmosphereComponent。
        """
        atm = world.get_world_entity().get_component(AtmosphereComponent)
        weather = world.get_world_entity().get_component(PhysicalWeatherComponent)

        if atm is None or weather is None:
            return

        temp = weather.temperature
        rh = weather.relative_humidity  # [0~1]
        pressure = weather.pressure

        # 1. 同步温度
        atm.temperature = temp

        # 2. 将相对湿度从 [0~1] 转换为 [0~100] 并同步
        atm.humidity = rh * 100.0

        # 3. 计算实际水汽压和绝对湿度
        e_actual = self.actual_vapor_pressure(temp, rh)
        ah = self.absolute_humidity_from_vapor_pressure(e_actual, temp)
        atm.water_vapor = ah / 1000.0  # g/m³ → kg/m³

        # 4. 计算空气密度（使用理想气体状态方程，考虑水汽修正）
        t_kelvin = max(80.15, temp + 273.15)
        p_pa = pressure * 100.0

        # 干空气密度
        rho_dry = p_pa / (self.R_DRY_AIR * t_kelvin)

        # 水汽修正（湿空气密度略低）
        # 简化为：ρ_moist = ρ_dry * (1 - 0.378 * e/P)
        if pressure > 0:
            rho_moist = rho_dry * (1.0 - 0.378 * e_actual / pressure)
        else:
            rho_moist = rho_dry

        atm.air_density = max(0.1, min(rho_moist, 3.0))
