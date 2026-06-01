#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
气候系统 — Ornstein-Uhlenbeck 随机过程版

不再使用 ElNino/LaNina/Neutral 等硬编码相位。
通过 OU 过程模拟气候的自然波动：
- 均值回归：趋势不会无限偏离
- 持续记忆：变化有惯性
- 无预设模式：不依赖任何命名气候现象
"""

import random
import math

from core.world import World
from core.system import System
from environment.climate.climate_component import ClimateComponent


class ClimateSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    气候趋势系统

    使用 Ornstein-Uhlenbeck 过程生成长期气候趋势：
        dx = -θ * x * dt + σ * dW
    其中 x 是趋势值，θ 是回归速率，σ 是波动强度，dW 是维纳过程增量。
    """

    # OU 过程参数
    THETA: float = 0.005       # 回归速率（每小时）
    SIGMA_TEMP: float = 0.008  # 温度趋势波动强度
    SIGMA_HUMID: float = 0.005 # 湿度趋势波动强度
    SIGMA_RAIN: float = 0.006  # 降雨趋势波动强度

    # 趋势有效范围
    TEMP_TREND_MIN: float = -3.0
    TEMP_TREND_MAX: float = 3.0
    HUMID_TREND_MIN: float = -0.2
    HUMID_TREND_MAX: float = 0.2
    RAIN_TREND_MIN: float = 0.7
    RAIN_TREND_MAX: float = 1.3

    def update(self, world: World, delta_hours: float):
        climate: ClimateComponent = world.get_world_entity().get_component(ClimateComponent)
        if climate is None:
            return

        dt = delta_hours

        # ── 温度趋势 OU 更新 ──
        climate._temp_velocity += (
            -self.THETA * climate.temp_trend * dt
            + random.gauss(0, self.SIGMA_TEMP * math.sqrt(dt))
        )
        climate.temp_trend += climate._temp_velocity * dt
        climate.temp_trend = max(
            self.TEMP_TREND_MIN,
            min(self.TEMP_TREND_MAX, climate.temp_trend)
        )
        # 速度阻尼防止爆炸
        climate._temp_velocity *= 0.95

        # ── 湿度趋势 OU 更新 ──
        climate._humidity_velocity += (
            -self.THETA * climate.humidity_trend * dt
            + random.gauss(0, self.SIGMA_HUMID * math.sqrt(dt))
        )
        climate.humidity_trend += climate._humidity_velocity * dt
        climate.humidity_trend = max(
            self.HUMID_TREND_MIN,
            min(self.HUMID_TREND_MAX, climate.humidity_trend)
        )
        climate._humidity_velocity *= 0.95

        # ── 降雨趋势 OU 更新 ──
        climate._rainfall_velocity += (
            -self.THETA * (climate.rainfall_trend - 1.0) * dt
            + random.gauss(0, self.SIGMA_RAIN * math.sqrt(dt))
        )
        climate.rainfall_trend += climate._rainfall_velocity * dt
        climate.rainfall_trend = max(
            self.RAIN_TREND_MIN,
            min(self.RAIN_TREND_MAX, climate.rainfall_trend)
        )
        climate._rainfall_velocity *= 0.95
