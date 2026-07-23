#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
风场系统 [v2.0] — 基于 PhysicalWeather 计算风场参数

【物理原理】
1. 气压梯度力驱动风
2. 温度差异产生热风
3. 科里奥利力影响风向

【数据流】
PhysicalWeatherComponent (wind_speed, pressure, temperature)
    → WindSystem
    → AtmosphereComponent (wind_speed, wind_direction)
"""

import random

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)


class WindSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    风场系统

    从 PhysicalWeatherComponent 读取风速，
    计算风向并同步到 AtmosphereComponent。
    """

    # 物理常量
    GROUND_TEMPERATURE = 15.0  # °C，用于计算温差
    STANDARD_PRESSURE = 1013.25  # hPa

    @staticmethod
    def calculate_pressure_gradient_force(pressure_change: float, distance: float = 100.0) -> float:
        """计算气压梯度力（简化）"""
        return pressure_change / distance if distance > 0 else 0

    @staticmethod
    def calculate_coriolis_deflection(wind_speed: float, latitude: float = 30.0) -> float:
        """计算科里奥利力导致的偏转（度）"""
        return 0.0001 * 2 * wind_speed * abs(latitude)

    def update(self, world: World, delta_hours: float):
        """
        风场系统更新

        数据流：PhysicalWeatherComponent → AtmosphereComponent
        """
        # 防御：使用 world.get_world_component 替代 entity.get_component
        atm = world.get_world_component(AtmosphereComponent)
        weather = world.get_world_component(PhysicalWeatherComponent)

        if atm is None or weather is None:
            return

        # 从物理天气模块读取风速
        wind_speed = weather.wind_speed
        pressure = weather.pressure
        temperature = weather.temperature

        # 1. 气压梯度贡献
        pressure_diff = pressure - self.STANDARD_PRESSURE
        pressure_gradient_force = abs(pressure_diff) * 0.4

        # 2. 温度差异贡献（热对流风）
        temp_diff = temperature - self.GROUND_TEMPERATURE
        thermal_wind = max(0, temp_diff) * 0.15

        # 3. 风速合成（以 PhysicalWeather 的风速为主，大气层做微调）
        # 气压梯度和热对流作为扰动叠加
        adjusted_speed = wind_speed + (pressure_gradient_force + thermal_wind) * 0.1
        atm.wind_speed = max(0, min(50, round(adjusted_speed, 2)))

        # 4. 风向计算
        # 以现有风向为基础，叠加气压梯度方向
        base_direction = atm.wind_direction if atm.wind_direction else random.uniform(0, 360)

        # 气压梯度方向：从高压指向低压（简化：正北为0，顺时针）
        if pressure_diff < 0:
            # 低压，风从四周吹入，方向随机偏移
            pressure_direction = random.uniform(0, 360)
        else:
            # 高压，风向外吹
            pressure_direction = (base_direction + 180) % 360

        # 科里奥利偏转
        coriolis = self.calculate_coriolis_deflection(atm.wind_speed)

        # 合成风向
        blend = 0.8  # 80% 保持原有风向，20% 受气压梯度影响
        new_direction = (base_direction * blend + pressure_direction * (1 - blend) + coriolis) % 360
        atm.wind_direction = round(new_direction, 1)