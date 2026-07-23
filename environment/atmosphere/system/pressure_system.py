#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件: pressure_system.py
@说明：气压系统 — 基于 PhysicalWeather 计算 ISA 标准大气参数
@时间：2026/04/25 10:00:00
@作者：Sherry
@版本：2.0 — 接入物理天气模块
'''

import math
import logging

from core.system import System
from core.world import World

logger = logging.getLogger(__name__)

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.atmosphere.system.atmosphere_physics_system import AtmospherePhysicsSystem
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)


class PressureSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    气压系统

    【职责】
    从 PhysicalWeatherComponent 读取温度与气压，
    基于 ISA 标准大气模型计算空气密度，同步到 AtmosphereComponent。

    【物理模型】
    理想气体状态方程：ρ = P / (R·T)
    - P 从 PhysicalWeatherComponent.pressure 读取 (hPa)
    - T 从 PhysicalWeatherComponent.temperature 读取 (°C)
    - R = 287.05 J/(kg·K)
    """

    # 干空气气体常数
    R_DRY_AIR = 287.05  # J/(kg·K)

    def update(self, world: World, delta_hours: float):
        """
        气压系统更新

        数据流：PhysicalWeatherComponent → AtmosphereComponent
        """
        # 防御：使用 world.get_world_component 替代 entity.get_component
        atm = world.get_world_component(AtmosphereComponent)
        weather = world.get_world_component(PhysicalWeatherComponent)

        if atm is None or weather is None:
            return

        # 同步温度与气压
        atm.temperature = weather.temperature
        atm.pressure = weather.pressure

        # 根据 ISA 模型重新计算海拔（反向推导，用于高海拔低氧等场景）
        # 这里使用简化模型：假设地面气压 = weather.pressure
        # 海拔对气压的影响已隐含在 PhysicalWeatherSystem 的气压演化中
        if atm.altitude > 0:
            isa_pressure = AtmospherePhysicsSystem.isa_pressure(atm.altitude)
            # 如果实际气压显著低于 ISA 标准，说明存在低压系统
            pressure_anomaly = weather.pressure - isa_pressure
            atm.pressure = weather.pressure
        else:
            atm.pressure = weather.pressure

        # 使用理想气体状态方程计算空气密度
        t_kelvin = max(80.15, weather.temperature + 273.15)
        p_pa = weather.pressure * 100.0
        atm.air_density = p_pa / (self.R_DRY_AIR * t_kelvin)

    def apply_pressure_anomaly(self, world: World, center_lon: float, center_lat: float,
                               pressure: float, radius: float = 500e3, strength: float = 1.0):
        """
        应用局部气压扰动（用于模拟低压系统、高压脊等）
        """
        logger.info(f"[PressureSystem] 应用气压扰动：中心({center_lon}, {center_lat})，气压变化 {pressure}hPa")