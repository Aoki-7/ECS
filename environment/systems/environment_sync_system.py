#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
环境同步系统 — 将 world-level 环境状态同步到单元格 EnvironmentComponent

【作用】
    将世界级的物理天气、光场、季节、时间状态同步到每个空间单元格的
    EnvironmentComponent，使所有单元格的环境参数反映当前真实环境。

【同步字段】
    时间：time_of_day, is_daytime, year_progress, season
    天气：temperature, air_temperature, humidity, air_humidity,
          precipitation, rainfall, wind_speed, wind_direction
    光照：light_level, par, photoperiod, dli
    土壤/派生：soil_temperature, vpd, day_night_temp_diff, water_stress_index

【设计原则】
    - 零硬编码天气假设：光照参数从 LightFieldSystem 输出推导。
    - 不重复实现物理过程：详细大气/土壤/污染参数由各自子模块维护。
    - 仅同步其他系统高频读取的聚合字段。

【运行顺序】
    应在 SolarPositionSystem、PhysicalWeatherSystem、LightFieldSystem、
    SeasonSystem 及土壤相关系统之后运行。
"""

from typing import Dict, Optional

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
from environment.season.season_component import SeasonComponent


# 太阳光谱 W/m² → PAR (μmol/m²/s) 转换系数
# 对平均太阳光谱，1 W/m² ≈ 4.57 μmol/m²/s PAR
# 参考：McCree (1972), Thimijan & Heins (1983)
_WATTS_TO_PAR: float = 4.57

# 夜间 PAR 基底（月光/星光，约 0.1-0.2 μmol/m²/s）
_NIGHT_PAR_FLOOR: float = 0.1

# PAR → light_level 的归一化系数（约 1200 μmol/m²/s 视为满光照）
_PAR_TO_LIGHT_LEVEL: float = 1.0 / 1200.0


class EnvironmentSyncSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    环境同步系统

    将天气系统、光场系统、季节系统、时间系统的状态同步到每个单元格的
    EnvironmentComponent。
    """

    def __init__(self):
        super().__init__()
        self._last_world_spatial_values: Optional[Dict[str, float]] = None

    def update(self, world: World, delta_hours: float):
        # 防御：使用 world.get_world_component 替代 entity.get_component
        weather = world.get_world_component(PhysicalWeatherComponent)
        if weather is None:
            return

        surface_light = world.get_world_component(SurfaceLightComponent)
        solar_pos = world.get_world_component(SolarPositionComponent)
        season = world.get_world_component(SeasonComponent)

        time = world.get_time()
        if time is None:
            return
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
        is_daytime = False
        photoperiod = 12.0
        if solar_pos is not None:
            is_daytime = solar_pos.elevation > 0.0
            photoperiod = solar_pos.day_length
            if not is_daytime:
                par = _NIGHT_PAR_FLOOR

        # 光照水平 0-1
        light_level = min(1.0, par * _PAR_TO_LIGHT_LEVEL)

        # 光周期：从太阳位置系统获取实际昼长
        if photoperiod is None:
            photoperiod = 12.0

        # 昼夜温差（云量阻尼后）
        effective_diurnal_range = DEFAULT_DIURNAL_RANGE * (
            1.0 - CLOUD_DAMPING_FACTOR * weather.cloud_cover
        )

        # 降水速率 mm/h → mm/day (24小时累加)
        rainfall_mm_day = weather.precipitation_rate * 24.0

        # 季节与年份进度
        year_progress = 0.0
        season_name = "spring"
        if season is not None:
            year_progress = season.year_progress / season.year_length_hours if season.year_length_hours else 0.0
            season_name = self._year_progress_to_season(year_progress)

        # ── 同步 world_entity 的环境组件（作为全球天气基准） ──
        world_env = world.get_environment()
        spatial_delta = None
        if world_env is not None:
            old_spatial = self._last_world_spatial_values
            self._sync_env(
                world_env, weather, vpd_kpa, par, light_level, photoperiod,
                is_daytime, hour, year_progress, season_name,
                effective_diurnal_range, rainfall_mm_day, delta_hours,
                is_cell=False
            )
            new_spatial = {
                "temperature": world_env.temperature,
                "air_temperature": world_env.air_temperature,
                "humidity": world_env.humidity,
                "air_humidity": world_env.air_humidity,
                "soil_moisture": world_env.soil_moisture,
                "soil_temperature": world_env.soil_temperature,
            }
            if old_spatial is not None:
                spatial_delta = {
                    k: new_spatial[k] - old_spatial[k]
                    for k in old_spatial
                }
            self._last_world_spatial_values = new_spatial

        # ── 同步普通单元格实体（保留空间变化，只跟随全球天气增量） ──
        for entity, (env,) in world.get_components(EnvironmentComponent):
            env: EnvironmentComponent
            if world_env is not None and env is world_env:
                continue
            self._sync_env(
                env, weather, vpd_kpa, par, light_level, photoperiod,
                is_daytime, hour, year_progress, season_name,
                effective_diurnal_range, rainfall_mm_day, delta_hours,
                is_cell=True
            )
            if spatial_delta is not None:
                self._apply_spatial_delta(env, spatial_delta)

    def _sync_env(
        self,
        env: EnvironmentComponent,
        weather: PhysicalWeatherComponent,
        vpd_kpa: float,
        par: float,
        light_level: float,
        photoperiod: float,
        is_daytime: bool,
        hour: float,
        year_progress: float,
        season_name: str,
        effective_diurnal_range: float,
        rainfall_mm_day: float,
        delta_hours: float,
        is_cell: bool = False,
    ):
        """将天气数据同步到单个 EnvironmentComponent

        Args:
            is_cell: 为 True 时表示普通空间单元格，不直接覆盖温度/湿度/土壤温度，
                     以保留环境连续统产生的局部空间变化。
        """
        # 时间
        env.time_of_day = hour
        env.is_daytime = is_daytime
        env.year_progress = year_progress
        env.season = season_name

        # 全球基准实体直接写入天气值；单元格保留局部变化，由增量逻辑修正
        if not is_cell:
            env.temperature = weather.temperature
            env.air_temperature = weather.temperature
            env.humidity = weather.relative_humidity
            env.air_humidity = weather.relative_humidity

        # 降水
        env.precipitation = rainfall_mm_day
        env.rainfall = rainfall_mm_day

        # 风场
        env.wind_speed = weather.wind_speed
        # wind_direction 暂无权威来源，保留原值

        # 光照
        env.par = par
        env.light_level = light_level
        env.photoperiod = photoperiod

        # 日累计光量（增量累加）
        # μmol/m²/s * h → mol/m²/day（除以 1,000,000 再乘以 3600 s/h = 0.0036）
        env.dli += env.par * delta_hours * 0.0036

        # 派生指数
        env.vpd = vpd_kpa
        env.day_night_temp_diff = effective_diurnal_range

        # 土壤温度（一阶滞后，缓慢跟随气温）：仅对全球基准实体直接写入
        if not is_cell:
            env.soil_temperature = env.soil_temperature * 0.95 + weather.temperature * 0.05

        # 水分胁迫指数（基于当前土壤湿度重新计算）
        env.water_stress_index = EnvironmentSyncSystem.calculate_water_stress_index(
            env.soil_moisture, env.field_capacity, env.wilting_point
        )

    def _apply_spatial_delta(self, env: EnvironmentComponent, spatial_delta: Dict[str, float]) -> None:
        """将全球天气增量应用到单元格，保持局部空间变化"""
        for k, delta in spatial_delta.items():
            if not hasattr(env, k):
                continue
            value = getattr(env, k) + delta
            if k in ("humidity", "air_humidity", "soil_moisture"):
                value = max(0.0, min(1.0, value))
            setattr(env, k, value)

    @staticmethod
    def initialize_component(env: EnvironmentComponent) -> None:
        """根据 EnvironmentComponent 的初始化参数计算派生字段"""
        env.is_daytime = env.par > 50.0
        env.water_stress_index = EnvironmentSyncSystem.calculate_water_stress_index(
            env.soil_moisture, env.field_capacity, env.wilting_point
        )

    @staticmethod
    def calculate_water_stress_index(soil_moisture: float, field_capacity: float,
                                       wilting_point: float) -> float:
        """根据土壤水分、田间持水量和萎蔫点计算水分胁迫指数"""
        if field_capacity > wilting_point:
            stress = (field_capacity - soil_moisture) / (field_capacity - wilting_point)
            return float(max(0.0, min(1.0, stress)))
        return 0.0

    @staticmethod
    def snapshot(env: EnvironmentComponent) -> dict:
        """快照 - 返回高频使用字段"""
        return {
            'time_of_day': env.time_of_day,
            'is_daytime': env.is_daytime,
            'year_progress': env.year_progress,
            'season': env.season,
            'temperature': env.temperature,
            'air_temperature': env.air_temperature,
            'humidity': env.humidity,
            'air_humidity': env.air_humidity,
            'precipitation': env.precipitation,
            'rainfall': env.rainfall,
            'wind_speed': env.wind_speed,
            'wind_direction': env.wind_direction,
            'light_level': env.light_level,
            'par': env.par,
            'photoperiod': env.photoperiod,
            'dli': env.dli,
            'soil_moisture': env.soil_moisture,
            'soil_temperature': env.soil_temperature,
            'water_stress_index': env.water_stress_index,
            'co2': env.co2,
            'o2': env.o2,
            'vpd': env.vpd,
            'day_night_temp_diff': env.day_night_temp_diff,
        }

    @staticmethod
    def _year_progress_to_season(year_progress: float) -> str:
        """将年进度 0-1 转换为季节名称"""
        y = year_progress % 1.0
        if y < 0.25:
            return "spring"
        elif y < 0.50:
            return "summer"
        elif y < 0.75:
            return "autumn"
        return "winter"