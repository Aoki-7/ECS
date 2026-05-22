#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管线集成测试 —— 数据流完整性、环境工厂、管线报告
"""

import io
import sys as _sys

from environment.tests.base import T, build_test_world, setup_weather_world


# ════════════════════════════════════════════════════════════
# 管线数据流
# ════════════════════════════════════════════════════════════


def test_pipeline_data_flow():
    """管线数据流完整性 — 从太阳位置到地表光照的完整链路"""
    print("\n[Pipeline] 管线数据流完整性测试")
    from environment.light_field.system.solar_position_system import SolarPositionSystem
    from environment.light_field.system.solar_radiation_system import SolarRadiationSystem
    from environment.light_field.system.light_atmosphere_coupling_system import (
        LightAtmosphereCouplingSystem,
    )
    from environment.light_field.system.light_field_system import LightFieldSystem
    from environment.light_field.components.solar_position_component import SolarPositionComponent
    from environment.light_field.components.solar_radiation_component import SolarRadiationComponent
    from environment.light_field.components.light_scatter_component import LightScatterComponent
    from environment.light_field.components.surface_light_component import SurfaceLightComponent
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.season.season_component import SeasonComponent
    from environment.climate.climate_component import ClimateComponent
    from environment.environment_component import EnvironmentComponent
    from time_module.time_component import TimeComponent

    world = build_test_world()
    world._world_entity.add_component(SolarPositionComponent())
    world._world_entity.add_component(SolarRadiationComponent())
    world._world_entity.add_component(LightScatterComponent())
    world._world_entity.add_component(SurfaceLightComponent())
    world._world_entity.add_component(PhysicalWeatherComponent())
    world._world_entity.add_component(SeasonComponent())
    world._world_entity.add_component(ClimateComponent())
    world._world_entity.add_component(EnvironmentComponent())

    systems = [
        SolarPositionSystem(),
        SolarRadiationSystem(),
        LightAtmosphereCouplingSystem(),
        LightFieldSystem(),
    ]
    for sys_inst in systems:
        world.add_system(sys_inst)

    time_comp = world.get_world_component(TimeComponent)
    time_comp.day_of_year = 80
    time_comp.hour = 12.0

    for sys_inst in systems:
        sys_inst.update(world, 1.0)

    sp = world._world_entity.get_component(SolarPositionComponent)
    T.ok(f"SolarPosition: elevation={sp.elevation:.1f}°") if sp.elevation > 0 else T.fail("太阳高度角应为正")

    sr = world._world_entity.get_component(SolarRadiationComponent)
    T.ok(f"SolarRadiation: TOA={sr.toa_radiation:.1f} W/m²") if sr.toa_radiation > 0 else T.fail("TOA 应为正")

    sl = world._world_entity.get_component(SurfaceLightComponent)
    T.ok(f"SurfaceLight: direct={sl.direct_light:.1f}, diffuse={sl.diffuse_light:.1f} W/m²")
    total = sl.direct_light + sl.diffuse_light
    T.ok(f"总地表辐射 {total:.1f} W/m² < TOA {sr.toa_radiation:.1f}") \
        if total < sr.toa_radiation else T.fail("地表辐射不应超过大气顶辐射")

    lfs = systems[-1]
    sr.toa_radiation = 0.0
    lfs.update(world, 1.0)
    T.ok(f"TOA=0 时: direct={sl.direct_light}, diffuse={sl.diffuse_light}") \
        if sl.direct_light == 0 and sl.diffuse_light == 0 else T.fail("TOA=0 时地表光照应为0")


def test_pipeline_weather_to_environment():
    """天气→环境同步管线 — EnvironmentSyncSystem"""
    print("\n[Pipeline] 天气→环境同步测试")
    from environment.systems.environment_sync_system import EnvironmentSyncSystem
    from environment.environment_component import EnvironmentComponent
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.environment_factory import EnvironmentFactory

    world = build_test_world()
    world._world_entity.add_component(EnvironmentComponent())
    world._world_entity.add_component(PhysicalWeatherComponent())

    factory = EnvironmentFactory(world)
    factory.create_environment_grid(3, 3)

    weather = world._world_entity.get_component(PhysicalWeatherComponent)
    weather.temperature = 30.0
    weather.relative_humidity = 0.8
    weather.precipitation_rate = 2.0
    weather.wind_speed = 5.0
    weather.cloud_cover = 0.7

    ess = EnvironmentSyncSystem()
    ess.update(world, 1.0)

    count = 0
    for entity, (env,) in world.get_components(EnvironmentComponent):
        count += 1
        if entity.id == -1:
            continue
        T.ok(f"单元格#{entity.id}: T={env.air_temperature:.1f}°C, "
             f"RH={env.air_humidity:.1%}, rain={env.rainfall:.2f}mm/d, "
             f"wind={env.wind_speed:.1f}m/s")
        break

    entity_count = 0
    for entity, (env,) in world.get_components(EnvironmentComponent):
        if entity.id >= 0:
            entity_count += 1
            if abs(env.air_temperature - 30.0) > 0.1:
                T.fail(f"单元格温度未同步: {env.air_temperature}")
                break
    T.ok(f"共 {entity_count} 个单元格已同步天气数据") if entity_count > 0 else T.fail("没有单元格被同步")


# ════════════════════════════════════════════════════════════
# 环境工厂
# ════════════════════════════════════════════════════════════


def test_environment_factory():
    """EnvironmentFactory — 环境实体创建"""
    print("\n[Pipeline] EnvironmentFactory 环境创建测试")
    from environment.environment_factory import EnvironmentFactory

    world = build_test_world()
    factory = EnvironmentFactory(world)

    eid = factory.create_environment_cell(0, 0)
    entity = world.query_entity(eid)
    T.ok(f"创建实体 #{eid}") if entity is not None else T.fail("实体创建失败")

    ids = factory.create_environment_grid(5, 5)
    T.ok(f"创建 5x5 网格: {len(ids)} 个实体") if len(ids) == 25 else T.fail(f"网格数量异常: {len(ids)}")

    rect_ids = factory.create_environment_rect(0, 0, 2, 3)
    expected = 3 * 4
    T.ok(f"创建矩形区域: {len(rect_ids)} 个 (期望 {expected})") \
        if len(rect_ids) == expected else T.fail(f"区域数量异常: {len(rect_ids)}")

    entity_0 = world.query_entity(ids[0])
    comps = list(world.components.keys())
    needed = {"SpaceComponent", "EnvironmentComponent", "SoilComponent", "TerrainComponent", "LightFieldComponent"}
    comp_names = {c.__name__ for c in comps}
    missing = needed - comp_names
    T.ok(f"组件完整性: 已创建 {len(comps)} 种组件") if not missing else T.fail(f"缺失组件: {missing}")


def test_factory_with_terrain_types():
    """EnvironmentFactory — 不同地形类型创建"""
    print("\n[Pipeline] 工厂不同地形测试")
    from environment.environment_factory import EnvironmentFactory
    from environment.soil.components.soil_component import SoilType
    from environment.terrain.config.terrain_types import TerrainType

    world = build_test_world()
    factory = EnvironmentFactory(world)

    terrain_cells = {}
    for tt in [TerrainType.PLAIN, TerrainType.HILL, TerrainType.FOREST, TerrainType.DESERT]:
        eid = factory.create_environment_cell(0, 0, terrain_type=tt, soil_type=SoilType.LOAM)
        terrain_cells[tt.value] = eid

    T.ok(f"成功创建 {len(terrain_cells)} 种地形类型实体") if len(terrain_cells) == 4 else T.fail("地形创建失败")

    soil_cells = {}
    for st in [SoilType.SAND, SoilType.LOAM, SoilType.CLAY]:
        eid = factory.create_environment_cell(1, 1, terrain_type=TerrainType.PLAIN, soil_type=st)
        soil_cells[st] = eid

    T.ok(f"成功创建 {len(soil_cells)} 种土壤类型实体") if len(soil_cells) == 3 else T.fail("土壤类型创建失败")
    T.ok(f"世界总实体数: {world.entity_count()}")


# ════════════════════════════════════════════════════════════
# 管线报告
# ════════════════════════════════════════════════════════════


def test_pipeline_report():
    """EnvironmentPipeline.report() — 管线结构输出"""
    print("\n[Pipeline] 管线报告测试")
    from environment.pipeline import EnvironmentPipeline
    from core.system import System

    class DummySystem(System):
        def update(self, world, delta_hours):
            pass

    entries = [
        (DummySystem(), "Dummy1", "input → output1"),
        (DummySystem(), "Dummy2", "input → output2"),
    ]
    pipeline = EnvironmentPipeline(entries)
    T.ok(f"管线有 {len(pipeline._entries)} 个条目") if len(pipeline._entries) == 2 else T.fail("条目数异常")

    report_text = pipeline.report()
    T.ok(f"report() 返回了管线结构: {len(report_text)} 字符") if len(report_text) > 20 else T.fail("report() 输出过短")
    T.ok("包含系统名称") if "Dummy1" in report_text else T.fail("report() 缺少系统名")


# ════════════════════════════════════════════════════════════
# 运行入口
# ════════════════════════════════════════════════════════════


def run():
    test_pipeline_data_flow()
    test_pipeline_weather_to_environment()
    test_environment_factory()
    test_factory_with_terrain_types()
    test_pipeline_report()


if __name__ == "__main__":
    run()
