#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
气候系统 V2 — 标准 Ornstein-Uhlenbeck 随机过程版

通过标准离散 OU 过程模拟气候的长期波动：
    x += θ * (μ - x) * dt + σ * sqrt(dt) * ξ

其中：
- x：当前趋势值
- μ：目标均值（由洋流、外部驱动、气候耦合共同决定）
- θ：回归速率
- σ * sqrt(dt) * ξ：高斯噪声

特性：
- 严格均值回归，避免无限偏离。
- 洋流仅影响目标均值，不再直接修改气候状态。
- 温度 → 湿度 → 降雨的弱耦合关系。
- 预留外部驱动扩展接口（火山、太阳活动、冰期等）。
"""

import random
import math

from core.world import World
from core.system import System
from environment.climate.climate_component import ClimateComponent
from environment.ocean.components.ocean_current_component import OceanCurrentComponent
from space.space_component import SpaceComponent
from core.sqrt_cache import cached_sqrt


class ClimateSystem(System):
    tick_interval = 2  # 每2帧执行一次

    # OU 过程参数
    THETA_TEMP: float = 0.003   # 温度回归速率（每小时）
    THETA_HUMID: float = 0.002  # 湿度回归速率（每小时）
    THETA_RAIN: float = 0.002   # 降雨回归速率（每小时）

    SIGMA_TEMP: float = 0.01    # 温度趋势波动强度
    SIGMA_HUMID: float = 0.006  # 湿度趋势波动强度
    SIGMA_RAIN: float = 0.008   # 降雨趋势波动强度

    # 趋势有效范围
    TEMP_TREND_MIN: float = -3.0
    TEMP_TREND_MAX: float = 3.0
    HUMID_TREND_MIN: float = -0.2
    HUMID_TREND_MAX: float = 0.2
    RAIN_TREND_MIN: float = 0.7
    RAIN_TREND_MAX: float = 1.3

    # 气候变量弱耦合系数
    TEMP_TO_HUMID_COEF: float = 0.05   # 温度 → 湿度
    HUMID_TO_RAIN_COEF: float = 0.4    # 湿度 → 降雨

    def update(self, world: World, delta_hours: float):
        climate: ClimateComponent = world.get_world_component(ClimateComponent)
        if climate is None:
            return

        dt = delta_hours

        # 1. 计算目标均值
        target_temp = self._compute_target_temperature(world, climate)
        target_humid = self._compute_target_humidity(world, climate)
        target_rain = self._compute_target_rainfall(world, climate)

        # 2. 执行 OU 更新
        self._update_temperature(climate, target_temp, dt)
        self._update_humidity(climate, target_humid, dt)
        self._update_rainfall(climate, target_rain, dt)

    # ------------------------------------------------------------------
    # 目标均值计算
    # ------------------------------------------------------------------

    def _compute_target_temperature(self, world: World, climate: ClimateComponent) -> float:
        """计算温度目标均值：基准 0 + 洋流影响 + 外部驱动。"""
        target = 0.0
        target += self._get_ocean_temperature_effect(world)
        target += self._get_external_temperature_forcing(world)
        return target

    def _compute_target_humidity(self, world: World, climate: ClimateComponent) -> float:
        """计算湿度目标均值：基准 0 + 温度影响。"""
        target = 0.0
        # 温度升高 → 蒸发增强 → 湿度目标提高
        target += climate.temp_trend * self.TEMP_TO_HUMID_COEF
        return target

    def _compute_target_rainfall(self, world: World, climate: ClimateComponent) -> float:
        """计算降雨目标均值：基准 1.0 + 湿度影响。"""
        target = 1.0
        # 湿度增加 → 降雨概率提高
        target += climate.humidity_trend * self.HUMID_TO_RAIN_COEF
        return target

    # ------------------------------------------------------------------
    # OU 更新
    # ------------------------------------------------------------------

    def _update_temperature(self, climate: ClimateComponent, target: float, dt: float) -> None:
        """温度趋势标准 OU 更新。"""
        noise = random.gauss(0, self.SIGMA_TEMP * cached_sqrt(dt))
        climate.temp_trend += self.THETA_TEMP * (target - climate.temp_trend) * dt + noise
        climate.temp_trend = self._clamp(
            climate.temp_trend, self.TEMP_TREND_MIN, self.TEMP_TREND_MAX
        )

    def _update_humidity(self, climate: ClimateComponent, target: float, dt: float) -> None:
        """湿度趋势标准 OU 更新。"""
        noise = random.gauss(0, self.SIGMA_HUMID * cached_sqrt(dt))
        climate.humidity_trend += self.THETA_HUMID * (target - climate.humidity_trend) * dt + noise
        climate.humidity_trend = self._clamp(
            climate.humidity_trend, self.HUMID_TREND_MIN, self.HUMID_TREND_MAX
        )

    def _update_rainfall(self, climate: ClimateComponent, target: float, dt: float) -> None:
        """降雨趋势标准 OU 更新。"""
        noise = random.gauss(0, self.SIGMA_RAIN * cached_sqrt(dt))
        climate.rainfall_trend += self.THETA_RAIN * (target - climate.rainfall_trend) * dt + noise
        climate.rainfall_trend = self._clamp(
            climate.rainfall_trend, self.RAIN_TREND_MIN, self.RAIN_TREND_MAX
        )

    # ------------------------------------------------------------------
    # 驱动源
    # ------------------------------------------------------------------

    def _get_ocean_temperature_effect(self, world: World) -> float:
        """
        洋流对目标温度的影响。

        暖流提高目标温度，寒流降低目标温度。
        影响施加在目标均值上，由 OU 过程缓慢逼近，避免状态永久累积。
        """
        effect = 0.0
        for entity, (current, space) in world.get_components(OceanCurrentComponent, SpaceComponent):
            if current is None:
                continue

            if current.current_type == "warm":
                effect += 0.5 * (current.temperature / 25.0)
            elif current.current_type == "cold":
                effect -= 0.5 * ((25.0 - current.temperature) / 25.0)

        return effect

    def _get_external_temperature_forcing(self, world: World) -> float:
        """
        外部温度驱动扩展接口。

        默认返回 0.0。
        未来可由 VolcanoSystem、SolarSystem、IceAgeSystem 等子类重写或注册驱动。
        """
        return 0.0

    # ------------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp(value: float, min_val: float, max_val: float) -> float:
        """将数值限制在 [min_val, max_val] 范围内。"""
        return max(min_val, min(max_val, value))
