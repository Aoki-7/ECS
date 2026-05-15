#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
环境构建器

作用:
    根据 EnvironmentProfile 自动为世界创建所有环境子系统。
    创建世界级的组件实例，构建系统管线。

管线注册顺序 (定义于 pipeline.py):
    LAYER 1: SolarPosition → SolarRadiation → Season → Climate
    LAYER 2: PhysicalWeather → AtmosphereCoupling → LightField
    LAYER 3: WeatherModifierBridge → WeatherEvent → WeatherLifetime
    LAYER 4: SoilTemperature → SoilWaterBalance → Soil → EnvironmentSync

注意:
    EnvironmentComponent 由 SimulationLoop 统一添加到世界实体，
    Builder 只负责创建和注册环境子系统。
"""

from typing import List, Tuple

from core.world import World
# ── 时间系统 ──
from time_module.time_system import TimeSystem
from core.system import System

from environment.pipeline import EnvironmentPipeline, PipelineEntry

# ── LAYER 1: 外部强迫 ──
from environment.light_field.system.solar_position_system import SolarPositionSystem
from environment.light_field.system.solar_radiation_system import SolarRadiationSystem
from environment.season.config.season_builder import SeasonBuilder
from environment.climate.config.climate_builder import ClimateBuilder

# ── LAYER 2: 大气物理 ──
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.physics_weather.systems.physical_weather_system import (
    PhysicalWeatherSystem,
)
from environment.light_field.system.light_atmosphere_coupling_system import (
    LightAtmosphereCouplingSystem,
)
from environment.light_field.system.light_field_system import LightFieldSystem

# ── LAYER 3: 极端事件 ──
from environment.physics_weather.systems.weather_modifier_bridge import (
    WeatherModifierBridgeSystem,
)
from environment.physics_weather.systems.weather_event_system import (
    WeatherEventSystem,
)
from environment.physics_weather.systems.weather_lifetime_system import (
    WeatherLifetimeSystem,
)

# ── LAYER 4: 地表层 ──
from environment.soil.systems.soil_temperature_system import SoilTemperatureSystem
from environment.soil.systems.soil_water_balance_system import SoilWaterBalanceSystem
from environment.soil.systems.soil_system import SoilSystem
from environment.systems.environment_sync_system import EnvironmentSyncSystem

# ── 光照模块组件 ──
from environment.light_field.components.solar_position_component import (
    SolarPositionComponent,
)
from environment.light_field.components.solar_radiation_component import (
    SolarRadiationComponent,
)
from environment.light_field.components.light_scatter_component import (
    LightScatterComponent,
)
from environment.light_field.components.surface_light_component import (
    SurfaceLightComponent,
)

# ── 土壤模块组件（world-level）──
from environment.soil.components.soil_temperature_component import (
    SoilTemperatureComponent,
)
from environment.soil.components.soil_moisture_component import (
    SoilMoistureComponent,
)


class EnvironmentBuilder:
    """
    环境构建器

    创建世界级组件 + 管线系统，返回 EnvironmentPipeline。
    """

    @staticmethod
    def build(world: World, profile=None) -> EnvironmentPipeline:
        # ── 1. 创建世界级环境组件 ──
        # 光照链路
        world._world_entity.add_component(SolarPositionComponent())
        world._world_entity.add_component(SolarRadiationComponent())
        world._world_entity.add_component(LightScatterComponent())
        world._world_entity.add_component(SurfaceLightComponent())

        # 土壤（world-level 基线，SoilTemperatureSystem/SoilWaterBalanceSystem 使用）
        world._world_entity.add_component(SoilTemperatureComponent())
        world._world_entity.add_component(SoilMoistureComponent())

        # ── 2. 调用各子模块 Builder ──
        # 季节系统（创建 SeasonComponent + 返回 SeasonSystem）
        season_systems = SeasonBuilder.build(world, profile)  # list[System]
        # 气候系统（创建 ClimateComponent + 返回 ClimateSystem）
        climate_systems = ClimateBuilder.build(world, profile)  # list[System]
        # 天气系统（创建 PhysicalWeatherComponent + 返回系统）
        weather_systems = EnvironmentBuilder._build_weather_systems(world, profile)

        # ── 3. 构建管线条目 ──
        entries: List[PipelineEntry] = []

        # LAYER 0 (时间推进 — 所有系统的前提)
        entries.append((TimeSystem(verbose=False),   "TimeSystem",
                        "TimeComponent 时间推进"))

        # LAYER 1
        entries.append((SolarPositionSystem(),       "SolarPosition",
                        "TimeComponent → SolarPositionComponent"))
        entries.append((SolarRadiationSystem(),      "SolarRadiation",
                        "SolarPosition → SolarRadiationComponent"))
        entries.extend((s, "Season",                 "Time → SeasonComponent")
                       for s in season_systems)
        entries.extend((s, "Climate",                "Time → ClimateComponent")
                       for s in climate_systems)

        # LAYER 2
        entries.extend((s, "PhysicalWeather",        "Season+Climate → PhysicalWeatherComponent")
                       for s in weather_systems)
        entries.append((LightAtmosphereCouplingSystem(), "AtmosphereCoupling",
                        "Atmo+Weather → LightScatterComponent"))
        entries.append((LightFieldSystem(),          "LightField",
                        "SolarRadiation+Scatter → SurfaceLightComponent"))

        # LAYER 3
        entries.append((WeatherModifierBridgeSystem(), "ModifierBridge",
                        "ModifierComponent → PhysicalWeatherComponent deltas"))
        entries.append((WeatherEventSystem(world),     "WeatherEventGen",
                        "PhysicalWeather → 创建极端事件"))
        entries.append((WeatherLifetimeSystem(),       "WeatherLifetime",
                        "清理过期事件实体"))

        # LAYER 4
        entries.append((SoilTemperatureSystem(),     "SoilTemperature",
                        "Weather.temp → SoilTemperatureComponent"))
        entries.append((SoilWaterBalanceSystem(),    "SoilWaterBalance",
                        "Weather.precip/temp → SoilMoistureComponent"))
        entries.append((SoilSystem(),                "Soil",
                        "EnvironmentComponent.air_temp → SoilComponent"))
        entries.append((EnvironmentSyncSystem(),     "EnvironmentSync",
                        "Weather+Light → per-cell EnvironmentComponent"))

        pipeline = EnvironmentPipeline(entries)
        return pipeline

    @staticmethod
    def _build_weather_systems(world: World, profile) -> List[System]:
        """构建物理天气系统族"""
        latitude = getattr(profile, "latitude", 35.0) if profile else 35.0
        elevation = getattr(profile, "elevation", 0.0) if profile else 0.0

        # PhysicalWeatherComponent 由天气系统负责挂载
        # (物理天气组件是 weather 模块的核心)
        world._world_entity.add_component(PhysicalWeatherComponent())

        weather = PhysicalWeatherSystem(latitude=latitude, elevation=elevation)
        return [weather]
