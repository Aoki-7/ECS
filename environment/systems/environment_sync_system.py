#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
环境同步系统 — PhysicalWeatherComponent → EnvironmentComponent

【作用】
    将世界级的物理天气状态（PhysicalWeatherComponent）同步到每个空间单元格的
    EnvironmentComponent，使所有单元格的环境参数反映当前真实天气。

【职责】
    - 温度同步：weather.temperature → env.air_temperature
    - 湿度同步：weather.relative_humidity → env.air_humidity
    - 降水同步：weather.precipitation_rate (mm/h) → env.rainfall (mm/day)
    - 风速同步：weather.wind_speed → env.wind_speed
    - 光照同步：云量衰减 → env.par
    - VPD 计算：从温度+相对湿度推导 env.vpd
    - 昼夜温差：从云量阻尼后的日较差推导

【运行顺序】
    应在所有物理天气更新系统之后运行。
"""

import math

from core.world import World
from core.system import System

from environment.environment_component import EnvironmentComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.physics_weather.config.physics_constants import (
    saturation_vapor_pressure,
    DEFAULT_DIURNAL_RANGE,
    CLOUD_DAMPING_FACTOR,
)

# 晴空基准 PAR (μmol/m²/s)
CLEAR_SKY_PAR: float = 500.0

# 云量对 PAR 的衰减系数（cloud_cover = 1 时 PAR 降到 20%）
CLOUD_PAR_ATTENUATION: float = 0.8


class EnvironmentSyncSystem(System):
    """
    环境同步系统

    将天气系统的物理状态同步到每个单元格的 EnvironmentComponent。
    """

    def update(self, world: World, delta_hours: float):
        weather = world._world_entity.get_component(PhysicalWeatherComponent)
        if weather is None:
            return

        time = world.get_time()
        hour = time.hour

        # ── 计算全局派生值 ──
        # 蒸汽压亏缺 VPD (kPa) = es * (1 - RH)
        es = saturation_vapor_pressure(weather.temperature)
        vpd = es * (1.0 - weather.relative_humidity)  # hPa
        vpd_kpa = vpd / 10.0  # hPa → kPa

        # 云量对光照的衰减因子
        # cloud=0 → factor=1.0; cloud=1 → factor=0.2
        light_factor = 1.0 - CLOUD_PAR_ATTENUATION * weather.cloud_cover
        cloud_par = CLEAR_SKY_PAR * light_factor

        # 昼夜温度差（云量阻尼后）
        effective_diurnal_range = DEFAULT_DIURNAL_RANGE * (
            1.0 - CLOUD_DAMPING_FACTOR * weather.cloud_cover
        )

        # 降水速率 mm/h → mm/day (24小时累加)
        rainfall_mm_day = weather.precipitation_rate * 24.0

        # ── 遍历所有单元格 ──
        for entity, (env,) in world.get_components(EnvironmentComponent):
            env: EnvironmentComponent

            # 温度
            env.air_temperature = weather.temperature

            # 土壤温度（一阶滞后，缓慢跟随气温）
            env.soil_temperature = env.soil_temperature * 0.95 + weather.temperature * 0.05

            # 昼夜温差
            env.day_night_temp_diff = effective_diurnal_range

            # 湿度
            env.air_humidity = weather.relative_humidity
            env.vpd = vpd_kpa

            # 光照
            env.par = cloud_par

            # 光周期（从时间系统获取）
            # 简化：日出(~6:00)到日落(~18:00)
            env.photoperiod = 12.0
            if 6 <= hour < 18:
                env.par = cloud_par
            else:
                env.par = max(5.0, cloud_par * 0.02)  # 夜间极低

            # 日累计光量（增量累加）
            env.dli += env.par * delta_hours * 0.0036  # μmol/m²/s * h → mol/m²/day

            # 风速
            env.wind_speed = weather.wind_speed

            # 降水 (mm/day)
            env.rainfall = rainfall_mm_day
