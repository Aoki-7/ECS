#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
环境构建器

作用：
    根据 EnvironmentProfile 自动为世界创建所有环境组件和系统管线。
    返回一个 EnvironmentPipeline 实例，统一编排所有子系统。

管线结构（4 层 DAG，14 系统）:
    Layer 1: 外部强迫
        0. SolarPositionSystem     Time → 太阳位置 (高度角, 方位角, 昼长)
        1. SolarRadiationSystem    太阳位置 → 大气顶辐射 (TOA)
        2. SeasonSystem            Time → 季节偏置 (温度/降雨/日照因子)
        3. ClimateSystem           Time → 气候偏移 (ENSO相位, 湿度/降雨偏置)

    Layer 2: 大气物理
        4. PhysicalWeatherSystem   季节+气候+太阳 → 连续天气物理量
        5. AtmosphereCouplingSystem 云量+湿度+气溶胶 → 光学散射参数
        6. LightFieldSystem        TOA辐射+散射 → 地表光照 (直射/散射)

    Layer 3: 极端事件 (覆盖层)
        7. WeatherModifierBridgeSystem   极端事件 modifier → 天气物理量叠加
        8. WeatherEventSystem           天气状态 → 极端事件创建
        9. WeatherLifetimeSystem        过期事件清理

    Layer 4: 地表层
       10. SoilTemperatureSystem    天气温度 → 土壤温度
       11. SoilWaterBalanceSystem   天气降水 → 土壤水分
       12. SoilSystem               环境温度 → 土壤养分/pH
       13. EnvironmentSyncSystem    天气+光照 → 单元格环境 (EnvironmentComponent)
"""


from core.world import World
from environment.pipeline import EnvironmentPipeline


class EnvironmentBuilder:
    """环境模块构建器"""

    @staticmethod
    def build(world: World) -> EnvironmentPipeline:
        """
        构建完整的环境管线。

        1. 添加所有 world-level 组件
        2. 创建 14 个子系统
        3. 包装为 EnvironmentPipeline

        Args:
            world: 当前世界实例

        Returns:
            EnvironmentPipeline 实例（含全部 14 系统）
        """
        # ════════════════════════════════════════════
        # 1. 添加 world-level 组件
        # ════════════════════════════════════════════
        we = world.get_world_entity()

        # 季节组件
        from environment.season.season_component import SeasonComponent
        if we.get_component(SeasonComponent) is None:
            we.add_component(SeasonComponent())

        # 气候组件
        from environment.climate.climate_component import ClimateComponent
        if we.get_component(ClimateComponent) is None:
            we.add_component(ClimateComponent())

        # 太阳位置 / 辐射 / 光散射 / 地表光照
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
        if we.get_component(SolarPositionComponent) is None:
            we.add_component(SolarPositionComponent())
        if we.get_component(SolarRadiationComponent) is None:
            we.add_component(SolarRadiationComponent())
        if we.get_component(LightScatterComponent) is None:
            we.add_component(LightScatterComponent())
        if we.get_component(SurfaceLightComponent) is None:
            we.add_component(SurfaceLightComponent())

        # 物理天气组件
        from environment.physics_weather.components.physical_weather_component import (
            PhysicalWeatherComponent,
        )
        if we.get_component(PhysicalWeatherComponent) is None:
            we.add_component(PhysicalWeatherComponent())

        # 大气组件（可选，用于散射耦合）
        from environment.atmosphere.components.atmosphere_component import (
            AtmosphereComponent,
        )
        if we.get_component(AtmosphereComponent) is None:
            we.add_component(AtmosphereComponent())

        # 土壤组件（世界级）
        from environment.soil.components.soil_moisture_component import (
            SoilMoistureComponent,
        )
        from environment.soil.components.soil_temperature_component import (
            SoilTemperatureComponent,
        )
        if we.get_component(SoilMoistureComponent) is None:
            we.add_component(SoilMoistureComponent())
        if we.get_component(SoilTemperatureComponent) is None:
            we.add_component(SoilTemperatureComponent())

        # 环境组件（世界级，供其他系统引用）
        from environment.environment_component import EnvironmentComponent
        if we.get_component(EnvironmentComponent) is None:
            we.add_component(EnvironmentComponent())

        # ════════════════════════════════════════════
        # 2. 创建所有系统并构建管线
        # ════════════════════════════════════════════
        entries = []

        # — Layer 1: 外部强迫 —
        from environment.light_field.system.solar_position_system import (
            SolarPositionSystem,
        )
        entries.append((
            SolarPositionSystem(),
            "SolarPosition",
            "Time → SolarPositionComponent (elevation, azimuth, day_length)",
        ))

        from environment.light_field.system.solar_radiation_system import (
            SolarRadiationSystem,
        )
        entries.append((
            SolarRadiationSystem(),
            "SolarRadiation",
            "SolarPositionComponent → SolarRadiationComponent (toa_radiation)",
        ))

        from environment.season.season_system import SeasonSystem
        entries.append((
            SeasonSystem(),
            "Season",
            "Time → SeasonComponent (temp_offset, rain_factor, sun_factor)",
        ))

        from environment.climate.climate_system import ClimateSystem
        entries.append((
            ClimateSystem(),
            "Climate",
            "Time → ClimateComponent (bias, phase)",
        ))

        # — Layer 2: 大气物理 —
        from environment.physics_weather.systems.physical_weather_system import (
            PhysicalWeatherSystem,
        )
        entries.append((
            PhysicalWeatherSystem(),
            "PhysicalWeather",
            "SeasonComponent + ClimateComponent → PhysicalWeatherComponent (T, P, RH, cloud, precip, wind)",
        ))

        from environment.light_field.system.light_atmosphere_coupling_system import (
            LightAtmosphereCouplingSystem,
        )
        entries.append((
            LightAtmosphereCouplingSystem(),
            "AtmosphereCoupling",
            "AtmosphereComponent + PhysicalWeatherComponent → LightScatterComponent",
        ))

        from environment.light_field.system.light_field_system import LightFieldSystem
        entries.append((
            LightFieldSystem(),
            "LightField",
            "SolarRadiationComponent + LightScatterComponent → SurfaceLightComponent",
        ))

        # — Layer 3: 极端事件 —
        from environment.physics_weather.systems.weather_modifier_bridge import (
            WeatherModifierBridgeSystem,
        )
        entries.append((
            WeatherModifierBridgeSystem(),
            "ModifierBridge",
            "WeatherModifierComponent → PhysicalWeatherComponent (叠加 deltas)",
        ))

        from environment.physics_weather.systems.weather_event_system import (
            WeatherEventSystem,
        )
        entries.append((
            WeatherEventSystem(world),
            "WeatherEventGen",
            "PhysicalWeatherComponent → WeatherModifierComponent (创建事件)",
        ))

        from environment.physics_weather.systems.weather_lifetime_system import (
            WeatherLifetimeSystem,
        )
        entries.append((
            WeatherLifetimeSystem(),
            "WeatherLifetime",
            "WeatherModifierComponent → 清理过期事件",
        ))

        # — Layer 4: 地表层 —
        from environment.soil.systems.soil_temperature_system import (
            SoilTemperatureSystem,
        )
        entries.append((
            SoilTemperatureSystem(),
            "SoilTemperature",
            "PhysicalWeatherComponent.temperature → SoilTemperatureComponent",
        ))

        from environment.soil.systems.soil_water_balance_system import (
            SoilWaterBalanceSystem,
        )
        entries.append((
            SoilWaterBalanceSystem(),
            "SoilWaterBalance",
            "PhysicalWeatherComponent.precip/temp → SoilMoistureComponent",
        ))

        from environment.soil.systems.soil_system import SoilSystem
        entries.append((
            SoilSystem(),
            "Soil",
            "EnvironmentComponent.air_temp → SoilComponent (N, P, K, pH)",
        ))

        from environment.systems.environment_sync_system import EnvironmentSyncSystem
        entries.append((
            EnvironmentSyncSystem(),
            "EnvironmentSync",
            "PhysicalWeatherComponent + SurfaceLightComponent → EnvironmentComponent (per-cell)",
        ))

        # — Layer 5: 环境连续统（空间平滑） —
        from environment.continuum.environmental_continuum_system import (
            EnvironmentalContinuumSystem,
        )
        entries.append((
            EnvironmentalContinuumSystem(
                neighborhood="moore",
                boundary="reflective",
            ),
            "Continuum",
            "相邻单元格扩散/平流/水流/自恢复 → 空间连续性与自适应性",
        ))

        # ════════════════════════════════════════════
        # 3. 包装为 Pipeline
        # ════════════════════════════════════════════
        return EnvironmentPipeline(entries)
