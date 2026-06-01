#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
环境同步系统 — PhysicalWeatherComponent + SurfaceLightComponent → EnvironmentComponent

【作用】
    将世界级的物理天气状态和光场计算结果同步到每个空间单元格的
    EnvironmentComponent，使所有单元格的环境参数反映当前真实天气。

【职责】
    - 温度同步：weather.temperature → env.air_temperature
    - 湿度同步：weather.relative_humidity → env.air_humidity
    - 降水同步：weather.precipitation_rate (mm/h) → env.rainfall (mm/day)
    - 风速同步：weather.wind_speed → env.wind_speed
    - 光照同步：SurfaceLightComponent → env.par（W/m² → μmol/m²/s）
    - 光周期同步：SolarPositionComponent.day_length → env.photoperiod
    - VPD 计算：从温度+相对湿度推导 env.vpd
    - 昼夜温差：从云量阻尼后的日较差推导

【设计原则】
    - 零硬编码天气假设：光照参数从 LightFieldSystem 输出推导，不独立计算。
    - 所有默认值从物理状态推导。

【运行顺序】
    应在所有物理天气更新系统和 LightFieldSystem 之后运行。
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
from environment.light_field.components.surface_light_component import (
    SurfaceLightComponent,
)
from environment.light_field.components.solar_position_component import (
    SolarPositionComponent,
)


# 太阳光谱 W/m² → PAR (μmol/m²/s) 转换系数
# 对平均太阳光谱，1 W/m² ≈ 4.57 μmol/m²/s PAR
# 参考：McCree (1972), Thimijan & Heins (1983)
_WATTS_TO_PAR: float = 4.57

# 夜间 PAR 基底（月光/星光，约 0.1-0.2 μmol/m²/s）
_NIGHT_PAR_FLOOR: float = 0.1


class EnvironmentSyncSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    环境同步系统

    将天气系统和光场系统的物理状态同步到每个单元格的 EnvironmentComponent。
    """

    def update(self, world: World, delta_hours: float):
        weather = world._world_entity.get_component(PhysicalWeatherComponent)
        if weather is None:
            return

        surface_light = world._world_entity.get_component(SurfaceLightComponent)
        solar_pos = world._world_entity.get_component(SolarPositionComponent)

        time = world.get_time()
        hour = time.hour

        # ── 计算全局派生值 ──
        # 蒸汽压亏缺 VPD (kPa) = es * (1 - RH)
        es = saturation_vapor_pressure(weather.temperature)
        vpd = es * (1.0 - weather.relative_humidity)  # hPa
        vpd_kpa = vpd / 10.0  # hPa → kPa

        # 光照：从 SurfaceLightComponent 推导 PAR
        if surface_light is not None:
            total_watts = surface_light.direct_light + surface_light.diffuse_light
            par = total_watts * _WATTS_TO_PAR
        else:
            # 极端 fallback：无光照数据时从云量推导（不应发生）
            par = 500.0 * (1.0 - 0.8 * weather.cloud_cover)

        # 夜间保护：当太阳在地平线以下时，PAR 降到夜间基底
        if solar_pos is not None and solar_pos.elevation <= 0.0:
            par = _NIGHT_PAR_FLOOR

        # 光周期：从太阳位置系统获取实际昼长
        photoperiod = solar_pos.day_length if solar_pos is not None else 12.0

        # 昼夜温度差（云量阻尼后）
        effective_diurnal_range = DEFAULT_DIURNAL_RANGE * (
            1.0 - CLOUD_DAMPING_FACTOR * weather.cloud_cover
        )

        # 降水速率 mm/h → mm/day (24小时累加)
        rainfall_mm_day = weather.precipitation_rate * 24.0

        # ── 同步 world_entity 的环境组件（供人类/生物系统读取） ──
        world_env = world.get_environment()
        if world_env is not None:
            self._sync_env(
                world_env, weather, vpd_kpa, par, photoperiod,
                effective_diurnal_range, rainfall_mm_day, delta_hours
            )

        # ── 遍历所有普通单元格实体 ──
        for entity, (env,) in world.get_components(EnvironmentComponent):
            env: EnvironmentComponent
            self._sync_env(
                env, weather, vpd_kpa, par, photoperiod,
                effective_diurnal_range, rainfall_mm_day, delta_hours
            )

    def _sync_env(
        self,
        env: EnvironmentComponent,
        weather: PhysicalWeatherComponent,
        vpd_kpa: float,
        par: float,
        photoperiod: float,
        effective_diurnal_range: float,
        rainfall_mm_day: float,
        delta_hours: float,
    ):
        """将天气数据同步到单个 EnvironmentComponent"""
        # 温度
        env.air_temperature = weather.temperature

        # 土壤温度（一阶滞后，缓慢跟随气温）
        env.soil_temperature = env.soil_temperature * 0.95 + weather.temperature * 0.05

        # 昼夜温差
        env.day_night_temp_diff = effective_diurnal_range

        # 湿度
        env.air_humidity = weather.relative_humidity
        env.vpd = vpd_kpa

        # 光照与光周期
        env.par = par
        env.photoperiod = photoperiod

        # 日累计光量（增量累加）
        # μmol/m²/s * h → mol/m²/day（除以 1,000,000 再乘以 3600 s/h = 0.0036）
        env.dli += env.par * delta_hours * 0.0036

        # 风速
        env.wind_speed = weather.wind_speed

        # 降水 (mm/day)
        env.rainfall = rainfall_mm_day
