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
        2. SeasonSystem            Time → 年份进度（无固定季节枚举）
        3. ClimateSystem           Time → 气候趋势 (OU 随机过程)

    Layer 2: 大气物理
        4. PhysicalWeatherSystem   天文参数+气候趋势 → 连续天气物理量
        5. AtmosphereCouplingSystem 云量+湿度+气溶胶 → 光学散射参数
        6. LightFieldSystem        TOA辐射+散射 → 地表光照 (直射/散射)

    Layer 3: 异常检测 (覆盖层)
        7. [预留] WeatherModifierBridgeSystem
        8. WeatherEventSystem      物理量统计 → 异常检测（无预定义事件类型）
        9. WeatherLifetimeSystem   异常记录清理

    Layer 4: 地表层
       10. SoilTemperatureSystem    天气温度 → 土壤温度
       11. SoilWaterBalanceSystem   天气降水 → 土壤水分
       12. SoilSystem               环境温度 → 土壤养分/pH
       13. EnvironmentSyncSystem    天气+光照 → 环境组件同步
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
        if world.get_world_component(SeasonComponent) is None:
            world.add_component(we, SeasonComponent())

        # 气候组件
        from environment.climate.climate_component import ClimateComponent
        if world.get_world_component(ClimateComponent) is None:
            world.add_component(we, ClimateComponent())

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
        if world.get_world_component(SolarPositionComponent) is None:
            world.add_component(we, SolarPositionComponent())
        if world.get_world_component(SolarRadiationComponent) is None:
            world.add_component(we, SolarRadiationComponent())
        if world.get_world_component(LightScatterComponent) is None:
            world.add_component(we, LightScatterComponent())
        if world.get_world_component(SurfaceLightComponent) is None:
            world.add_component(we, SurfaceLightComponent())

        # 物理天气组件
        from environment.physics_weather.components.physical_weather_component import (
            PhysicalWeatherComponent,
        )
        if world.get_world_component(PhysicalWeatherComponent) is None:
            world.add_component(we, PhysicalWeatherComponent())

        # 大气组件（可选，用于散射耦合）
        from environment.atmosphere.components.atmosphere_component import (
            AtmosphereComponent,
        )
        if world.get_world_component(AtmosphereComponent) is None:
            world.add_component(we, AtmosphereComponent())

        # 土壤组件（世界级）
        from environment.soil.components.soil_moisture_component import (
            SoilMoistureComponent,
        )
        from environment.soil.components.soil_temperature_component import (
            SoilTemperatureComponent,
        )
        if world.get_world_component(SoilMoistureComponent) is None:
            world.add_component(we, SoilMoistureComponent())
        if world.get_world_component(SoilTemperatureComponent) is None:
            world.add_component(we, SoilTemperatureComponent())

        # 环境组件（世界级，供其他系统引用）
        from environment.environment_component import EnvironmentComponent
        if world.get_world_component(EnvironmentComponent) is None:
            world.add_component(we, EnvironmentComponent())

        # 重力组件（环境属性）
        from environment.components.gravity_component import GravityComponent
        if world.get_world_component(GravityComponent) is None:
            world.add_component(we, GravityComponent(acceleration=9.8))

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

        # 大气微观物理层（辅助天气模块，基于 PhysicalWeather 计算精细大气参数）
        from environment.atmosphere.system.atmosphere_system import AtmosphereSystem
        entries.append((
            AtmosphereSystem(),
            "Atmosphere",
            "PhysicalWeatherComponent → AtmosphereComponent (ISA气压, 空气密度, 风场, 对流, 云密度)",
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

        from environment.physics_weather.systems.weather_event_system import (
            WeatherEventSystem,
        )
        entries.append((
            WeatherEventSystem(),
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