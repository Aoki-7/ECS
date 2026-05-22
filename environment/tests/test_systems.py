#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统单元测试 —— 所有独立环境系统的输入/输出行为验证
"""

from environment.tests.base import T, build_test_world, setup_weather_world, setup_light_world


# ════════════════════════════════════════════════════════════
# 季节与气候系统
# ════════════════════════════════════════════════════════════


def test_season_system():
    """SeasonSystem — 年份进度推进"""
    print("\n[System] SeasonSystem 单元测试")
    from environment.season.season_system import SeasonSystem
    from environment.season.season_component import SeasonComponent

    world = build_test_world()
    world._world_entity.add_component(SeasonComponent())
    ss = SeasonSystem()

    season = world._world_entity.get_component(SeasonComponent)
    before = season.year_progress
    ss.update(world, 24.0)

    T.ok(f"年份进度 {before} → {season.year_progress}h") \
        if season.year_progress == before + 24.0 else T.fail("年份进度未推进")

    # 测试循环
    season.year_progress = season.year_length_hours - 10.0
    ss.update(world, 20.0)
    T.ok(f"跨年后 progress={season.year_progress}h (< year_length)") \
        if season.year_progress < season.year_length_hours else T.fail("年份循环异常")


def test_climate_system():
    """ClimateSystem — OU 随机过程趋势更新"""
    print("\n[System] ClimateSystem 单元测试")
    from environment.climate.climate_system import ClimateSystem
    from environment.climate.climate_component import ClimateComponent

    cs = ClimateSystem()
    world = setup_weather_world(build_test_world())
    cs.update(world, 24 * 100)

    climate = world._world_entity.get_component(ClimateComponent)
    T.ok(f"temp_trend={climate.temp_trend:+.2f}°C, humidity_trend={climate.humidity_trend:+.3f}, "
         f"rainfall_trend={climate.rainfall_trend:.3f}")
    T.ok("温度趋势在 [-3, 3]") if -3 <= climate.temp_trend <= 3 else T.fail("温度趋势越界")
    T.ok("降雨趋势在 [0.7, 1.3]") if 0.7 <= climate.rainfall_trend <= 1.3 else T.fail("降雨趋势越界")


# ════════════════════════════════════════════════════════════
# 太阳位置与辐射系统
# ════════════════════════════════════════════════════════════


def test_solar_position_system():
    """SolarPositionSystem — 太阳位置计算"""
    print("\n[System] SolarPositionSystem 单元测试")
    from environment.light_field.system.solar_position_system import SolarPositionSystem
    from environment.light_field.components.solar_position_component import SolarPositionComponent
    from time_module.time_component import TimeComponent

    world = build_test_world()
    world._world_entity.add_component(SolarPositionComponent())
    sps = SolarPositionSystem()
    time_comp = world.get_world_component(TimeComponent)

    time_comp.day_of_year = 172
    time_comp.hour = 12.0
    sps.update(world, 0)
    sp = world._world_entity.get_component(SolarPositionComponent)

    T.ok(f"夏至正午: elevation={sp.elevation:.1f}°, day_length={sp.day_length:.1f}h")
    T.ok(f"昼长 > 12h (夏季)") if sp.day_length > 12.0 else T.fail("夏至昼长异常")

    time_comp.day_of_year = 355
    sps.update(world, 0)
    T.ok(f"冬至正午: elevation={sp.elevation:.1f}°, day_length={sp.day_length:.1f}h")
    T.ok(f"昼长 < 12h (冬季)") if sp.day_length < 12.0 else T.fail("冬至昼长异常")

    night_elevation = sp.elevation
    T.ok(f"冬至中午仍可判断: elevation={night_elevation:.1f}° 且 < 夏季") if night_elevation < 78 else T.fail("冬至高度角异常")


def test_solar_radiation_system():
    """SolarRadiationSystem — 辐射计算"""
    print("\n[System] SolarRadiationSystem 单元测试")
    from environment.light_field.system.solar_radiation_system import SolarRadiationSystem
    from environment.light_field.system.solar_position_system import SolarPositionSystem
    from environment.light_field.components.solar_position_component import SolarPositionComponent
    from environment.light_field.components.solar_radiation_component import SolarRadiationComponent
    from time_module.time_component import TimeComponent

    world = build_test_world()
    world._world_entity.add_component(SolarPositionComponent())
    world._world_entity.add_component(SolarRadiationComponent())

    sps = SolarPositionSystem()
    srs = SolarRadiationSystem()
    time_comp = world.get_world_component(TimeComponent)

    time_comp.day_of_year = 80
    time_comp.hour = 12.0
    sps.update(world, 0)
    srs.update(world, 0)
    sr = world._world_entity.get_component(SolarRadiationComponent)
    T.ok(f"正午 TOA 辐射 = {sr.toa_radiation:.1f} W/m²")
    T.ok(f"TOA > 0") if sr.toa_radiation > 0 else T.fail("正午 TOA 应为正")


# ════════════════════════════════════════════════════════════
# 光场系统
# ════════════════════════════════════════════════════════════


def test_light_atmosphere_coupling_system():
    """LightAtmosphereCouplingSystem — 大气-光耦合"""
    print("\n[System] LightAtmosphereCouplingSystem 单元测试")
    from environment.light_field.system.light_atmosphere_coupling_system import (
        LightAtmosphereCouplingSystem,
    )
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.light_field.components.light_scatter_component import LightScatterComponent

    world = build_test_world()
    world._world_entity.add_component(PhysicalWeatherComponent())
    world._world_entity.add_component(LightScatterComponent())

    lacs = LightAtmosphereCouplingSystem()
    lacs.update(world, 1.0)

    scatter = world._world_entity.get_component(LightScatterComponent)
    T.ok(f"Rayleigh={scatter.rayleigh_factor:.4f}, Mie={scatter.mie_factor:.4f}, "
         f"cloud_attn={scatter.cloud_attenuation:.4f}")
    T.ok(f"散射因子在合理范围") if 0 <= scatter.rayleigh_factor <= 0.5 else T.fail("Rayleigh 异常")


def test_light_field_system():
    """LightFieldSystem — 地表光照合成"""
    print("\n[System] LightFieldSystem 单元测试")
    from environment.light_field.system.light_field_system import LightFieldSystem
    from environment.light_field.components.solar_radiation_component import SolarRadiationComponent
    from environment.light_field.components.light_scatter_component import LightScatterComponent
    from environment.light_field.components.surface_light_component import SurfaceLightComponent

    world = build_test_world()
    world._world_entity.add_component(SolarRadiationComponent())
    world._world_entity.add_component(LightScatterComponent())
    world._world_entity.add_component(SurfaceLightComponent())

    sr = world._world_entity.get_component(SolarRadiationComponent)
    ls = world._world_entity.get_component(LightScatterComponent)
    sr.toa_radiation = 1000.0
    ls.rayleigh_factor = 0.1
    ls.mie_factor = 0.05
    ls.cloud_attenuation = 0.3

    lfs = LightFieldSystem()
    lfs.update(world)

    sl = world._world_entity.get_component(SurfaceLightComponent)
    T.ok(f"direct={sl.direct_light:.1f}, diffuse={sl.diffuse_light:.1f} W/m²")
    T.ok(f"直射光 > 0") if sl.direct_light > 0 else T.fail("强辐射时直射光应为正")

    sr.toa_radiation = 0
    lfs.update(world)
    T.ok(f"夜间 direct={sl.direct_light}, diffuse={sl.diffuse_light}") \
        if sl.direct_light == 0 and sl.diffuse_light == 0 else T.fail("夜间应为0")


# ════════════════════════════════════════════════════════════
# 天气物理系统
# ════════════════════════════════════════════════════════════


def test_physical_weather_system():
    """PhysicalWeatherSystem — 天气物理演化"""
    print("\n[System] PhysicalWeatherSystem 单步测试")
    from environment.physics_weather.systems.physical_weather_system import PhysicalWeatherSystem
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.physics_weather.config.physics_constants import (
        ABSOLUTE_HUMIDITY_MIN, ABSOLUTE_HUMIDITY_MAX,
        PRESSURE_MIN, PRESSURE_MAX, WIND_BASELINE,
    )
    from time_module.time_component import TimeComponent

    world = setup_weather_world(build_test_world())
    pws = PhysicalWeatherSystem(latitude=35.0)

    weather = world._world_entity.get_component(PhysicalWeatherComponent)
    before = weather.temperature, weather.pressure, weather.relative_humidity
    T.ok(f"初始: T={before[0]:.1f}°C, P={before[1]:.0f}hPa, RH={before[2]:.1%}")

    time_comp = world.get_world_component(TimeComponent)
    time_comp.hour = 12.0
    time_comp.day_of_year = 80
    pws.update(world, 1.0)

    after = weather.temperature, weather.pressure, weather.relative_humidity
    T.ok(f"1h后: T={after[0]:.1f}°C, P={after[1]:.0f}hPa, RH={after[2]:.1%}")
    T.ok(f"温度在合理范围 [-30, 50]") if -30 <= weather.temperature <= 50 else T.fail(f"温度越界: {weather.temperature}")
    T.ok(f"气压在合理范围 [{PRESSURE_MIN}, {PRESSURE_MAX}]") \
        if PRESSURE_MIN <= weather.pressure <= PRESSURE_MAX else T.fail(f"气压越界: {weather.pressure}")
    T.ok(f"绝对湿度在合理范围 [{ABSOLUTE_HUMIDITY_MIN}, {ABSOLUTE_HUMIDITY_MAX}]") \
        if ABSOLUTE_HUMIDITY_MIN <= weather.absolute_humidity <= ABSOLUTE_HUMIDITY_MAX \
        else T.fail(f"绝对湿度越界: {weather.absolute_humidity}")
    T.ok(f"云量在 [0,1]") if 0 <= weather.cloud_cover <= 1 else T.fail(f"云量越界: {weather.cloud_cover}")
    T.ok(f"风速在合理范围 [{WIND_BASELINE * 0.1}, 50]") if 0 <= weather.wind_speed <= 50 \
        else T.fail(f"风速越界: {weather.wind_speed}")
    T.ok(f"降水率 ≥ 0") if weather.precipitation_rate >= 0 else T.fail(f"降水率负数: {weather.precipitation_rate}")
    T.ok(f"RH={weather.relative_humidity:.4f} ∈ [0,1]") \
        if 0 <= weather.relative_humidity <= 1 else T.fail(f"RH 越界: {weather.relative_humidity}")


# ════════════════════════════════════════════════════════════
# 土壤系统
# ════════════════════════════════════════════════════════════


def test_soil_system():
    """SoilSystem — 土壤养分与pH演化"""
    print("\n[System] SoilSystem 单元测试")
    from environment.soil.systems.soil_system import SoilSystem
    from environment.soil.components.soil_component import SoilComponent

    world = build_test_world()
    entity = world.create_entity()
    soil = SoilComponent(moisture=0.5, nitrogen=100.0, phosphorus=40.0, potassium=80.0, ph=6.5)
    world.add_component(entity, soil)

    ss = SoilSystem()
    ss.update(world, 24.0)

    T.ok(f"1天后: 氮={soil.nitrogen:.1f}, 磷={soil.phosphorus:.1f}, 钾={soil.potassium:.1f}, pH={soil.ph:.2f}")
    T.ok(f"养分自然消耗") if soil.nitrogen < 100.0 else T.fail("氮未消耗")
    T.ok(f"湿度在 [凋萎点, 饱和含水量]") \
        if soil.wilting_point <= soil.moisture <= soil.saturation else T.fail(f"湿度越界: {soil.moisture}")
    T.ok(f"温度在合理范围") if -10 <= soil.temperature <= 50 else T.fail(f"土壤温度异常: {soil.temperature}°C")


def test_soil_water_balance_system():
    """SoilWaterBalanceSystem — 土壤水分平衡"""
    print("\n[System] SoilWaterBalanceSystem 单元测试")
    from environment.soil.systems.soil_water_balance_system import SoilWaterBalanceSystem
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.soil.components.soil_moisture_component import SoilMoistureComponent

    world = build_test_world()
    world._world_entity.add_component(PhysicalWeatherComponent())
    world._world_entity.add_component(SoilMoistureComponent())

    weather = world._world_entity.get_component(PhysicalWeatherComponent)
    soil = world._world_entity.get_component(SoilMoistureComponent)

    weather.precipitation_rate = 5.0
    weather.temperature = 25.0
    soil.moisture = 0.3
    soil.capacity = 1.0

    swbs = SoilWaterBalanceSystem()
    swbs.update(world, 1.0)

    T.ok(f"降雨后 moisture={soil.moisture:.4f} (期望 > 0.3)") if soil.moisture > 0.3 else T.fail("降雨后湿度未增加")
    T.ok(f"湿度 ≤ capacity ({soil.capacity})") if soil.moisture <= soil.capacity else T.fail("湿度超过持水能力")


def test_soil_temperature_system():
    """SoilTemperatureSystem — 土壤温度跟随"""
    print("\n[System] SoilTemperatureSystem 单元测试")
    from environment.soil.systems.soil_temperature_system import SoilTemperatureSystem
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.soil.components.soil_temperature_component import SoilTemperatureComponent

    world = build_test_world()
    world._world_entity.add_component(PhysicalWeatherComponent())
    world._world_entity.add_component(SoilTemperatureComponent())

    weather = world._world_entity.get_component(PhysicalWeatherComponent)
    soil = world._world_entity.get_component(SoilTemperatureComponent)

    weather.temperature = 35.0
    soil.temperature = 15.0

    sts = SoilTemperatureSystem()
    for _ in range(10):
        sts.update(world, 1.0)

    T.ok(f"土壤温度 {soil.temperature:.2f}°C 趋向气温 35°C") \
        if soil.temperature > 25 else T.fail(f"土壤温度未充分跟随: {soil.temperature}")


# ════════════════════════════════════════════════════════════
# 运行入口
# ════════════════════════════════════════════════════════════


def run():
    test_season_system()
    test_climate_system()
    test_solar_position_system()
    test_solar_radiation_system()
    test_light_atmosphere_coupling_system()
    test_light_field_system()
    test_physical_weather_system()
    test_soil_system()
    test_soil_water_balance_system()
    test_soil_temperature_system()


if __name__ == "__main__":
    run()
