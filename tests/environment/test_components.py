#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件单元测试 —— 所有环境相关组件的创建、属性、边界值、序列化
"""

from tests.environment.base import T, build_test_world

# ---------------------------------------------
# 核心环境组件
# ---------------------------------------------


def test_environment_component():
    """EnvironmentComponent — 创建、属性、边界值"""
    print("\n[Component] EnvironmentComponent 单元测试")
    from environment.environment_component import EnvironmentComponent

    e = EnvironmentComponent()
    T.ok(f"默认 PAR={e.par}, 温度={e.air_temperature}°C, 湿度={e.soil_moisture}") \
        if e.par == 300.0 and e.air_temperature == 25.0 and e.soil_moisture == 0.35 \
        else T.fail("默认值不正确")

    day = EnvironmentComponent(par=500.0)
    night = EnvironmentComponent(par=30.0)
    T.ok(f"PAR>50 判断为白天 ({day.par} → {day.is_daytime})") if day.is_daytime else T.fail("白天判断错误")
    T.ok(f"PAR≤50 判断为夜晚 ({night.par} → {night.is_daytime})") if not night.is_daytime else T.fail("夜晚判断错误")

    e1 = EnvironmentComponent(soil_moisture=0.45, field_capacity=0.45, wilting_point=0.15)
    T.ok(f"田间持水量时胁迫指数={e1.water_stress_index} (应为0)") if e1.water_stress_index == 0.0 else T.fail("水分胁迫指数错误")

    e2 = EnvironmentComponent(soil_moisture=0.15, field_capacity=0.45, wilting_point=0.15)
    T.ok(f"凋萎点时胁迫指数={e2.water_stress_index} (应为1)") if e2.water_stress_index == 1.0 else T.fail("凋萎点胁迫指数错误")

    e3 = EnvironmentComponent(soil_moisture=0.30, field_capacity=0.45, wilting_point=0.15)
    expected = (0.45 - 0.30) / (0.45 - 0.15)
    T.ok(f"中间水分胁迫指数={e3.water_stress_index:.2f} (应为{expected:.2f})") \
        if abs(e3.water_stress_index - expected) < 0.01 else T.fail("中间胁迫指数错误")

    snap = e.snapshot()
    T.ok(f"snapshot() 返回 {len(snap)} 个字段") if len(snap) >= 18 else T.fail("snapshot 字段不足")

    extreme = EnvironmentComponent(air_temperature=-50.0, soil_moisture=1.5, co2=10000.0)
    T.ok(f"极端值设置正常") if extreme.air_temperature == -50.0 else T.fail("极端值设置异常")


def test_physical_weather_component():
    """PhysicalWeatherComponent — 创建、序列化、边界"""
    print("\n[Component] PhysicalWeatherComponent 单元测试")
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )

    default = PhysicalWeatherComponent()
    T.ok(f"默认: T={default.temperature}°C, P={default.pressure}hPa, RH={default.relative_humidity:.0%}")
    d = default.to_dict()
    T.ok(f"to_dict 返回 {len(d)} 字段: {list(d.keys())}")

    extreme = PhysicalWeatherComponent(
        temperature=50.0, pressure=1060.0, wind_speed=50.0,
        precipitation_rate=50.0, cloud_cover=1.0,
    )
    T.ok(f"极端高温/高压/大风: {extreme}")
    d = extreme.to_dict()
    T.ok(f"序列化后温度={d['temperature']}") if d['temperature'] == 50.0 else T.fail("序列化错误")


def test_season_component():
    """SeasonComponent — 创建、年份进度推进"""
    print("\n[Component] SeasonComponent 单元测试")
    from environment.season.season_component import SeasonComponent

    s = SeasonComponent()
    T.ok(f"默认 year_length={s.year_length_hours}h, progress={s.year_progress}h")

    # 推进年份进度
    s.year_progress += 24.0
    T.ok(f"推进24h后 progress={s.year_progress}h") if s.year_progress == 24.0 else T.fail("年份进度未推进")

    # 循环
    s.year_progress = s.year_length_hours + 10.0
    # SeasonSystem 会处理循环，组件本身不自动循环
    T.ok(f"to_dict: {s.to_dict()}")


def test_climate_component():
    """ClimateComponent — 创建、趋势值"""
    print("\n[Component] ClimateComponent 单元测试")
    from environment.climate.climate_component import ClimateComponent

    c = ClimateComponent()
    T.ok(f"默认: temp_trend={c.temp_trend}, humidity_trend={c.humidity_trend}, rainfall_trend={c.rainfall_trend}")
    T.ok("趋势值在合理范围") if -3 <= c.temp_trend <= 3 and 0.7 <= c.rainfall_trend <= 1.3 else T.fail("默认趋势异常")


# ---------------------------------------------
# 光照组件
# ---------------------------------------------


def test_light_components():
    """光照组件 — SolarPosition / SolarRadiation / LightScatter / SurfaceLight"""
    print("\n[Component] 光照组件单元测试")
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

    sp = SolarPositionComponent()
    T.ok(f"SolarPosition: elevation={sp.elevation}, azimuth={sp.azimuth}, day_length={sp.day_length}")

    sr = SolarRadiationComponent()
    T.ok(f"SolarRadiation: solar_constant={sr.solar_constant}, toa={sr.toa_radiation}")

    ls = LightScatterComponent()
    T.ok(f"LightScatter: rayleigh={ls.rayleigh_factor}, mie={ls.mie_factor}, cloud_attn={ls.cloud_attenuation}")

    sl = SurfaceLightComponent()
    T.ok(f"SurfaceLight: direct={sl.direct_light}, diffuse={sl.diffuse_light}")


# ---------------------------------------------
# 土壤组件
# ---------------------------------------------


def test_soil_components():
    """土壤组件 — SoilComponent / SoilMoisture / SoilTemperature"""
    print("\n[Component] 土壤组件单元测试")
    from environment.soil.components.soil_component import SoilComponent, SoilType
    from environment.soil.components.soil_moisture_component import SoilMoistureComponent
    from environment.soil.components.soil_temperature_component import SoilTemperatureComponent

    sc = SoilComponent()
    T.ok(f"SoilComponent: type={sc.soil_type}, moisture={sc.moisture}, pH={sc.ph}")
    T.ok(f"to_dict 返回 {len(sc.to_dict())} 字段") if len(sc.to_dict()) == 10 else T.fail("soil to_dict 字段数不符")

    sm = SoilMoistureComponent()
    T.ok(f"SoilMoisture: moisture={sm.moisture}, capacity={sm.capacity}")

    st = SoilTemperatureComponent()
    T.ok(f"SoilTemperature: {st.temperature}°C")


# ---------------------------------------------
# 地形组件
# ---------------------------------------------


def test_terrain_component():
    """TerrainComponent + TerrainType — 创建、枚举、分组"""
    print("\n[Component] 地形组件测试")
    from environment.terrain.components.terrain_component import TerrainComponent
    from environment.terrain.config.terrain_types import (
        TerrainType, TERRAIN_GROUPS, is_water_terrain, is_land_terrain,
    )

    tc = TerrainComponent()
    T.ok(f"默认: elevation={tc.elevation}m, slope={tc.slope}°, aspect={tc.aspect}°")

    mountain = TerrainComponent(elevation=3000, slope=45, roughness=0.8, terrain_type=TerrainType.MOUNTAIN)
    T.ok(f"山地: {mountain.to_dict()}")

    T.ok(f"TerrainType 有 {len(TerrainType)} 个成员") if len(TerrainType) >= 10 else T.fail("TerrainType 枚举数不足")

    for tt in TerrainType:
        T.ok(f"  {tt.value} → {str(tt)}")

    T.ok(f"陆地地形 {len(TERRAIN_GROUPS['land'])} 种")
    T.ok(f"水域地形 {len(TERRAIN_GROUPS['water'])} 种")
    T.ok("PLAIN 是陆地") if is_land_terrain(TerrainType.PLAIN) else T.fail("PLAIN 应为陆地")
    T.ok("OCEAN 是水域") if is_water_terrain(TerrainType.OCEAN) else T.fail("OCEAN 应为水域")
    T.ok("DESERT 不是水域") if not is_water_terrain(TerrainType.DESERT) else T.fail("DESERT 不应是水域")


# ---------------------------------------------
# 光照扩展组件
# ---------------------------------------------


def test_light_field_component():
    """LightFieldComponent — 创建、光谱、阴影"""
    print("\n[Component] 光场组件测试")
    from environment.light_field.components.light_field_component import LightFieldComponent

    lfc = LightFieldComponent()
    T.ok(f"默认: PAR={lfc.par:.0f}, total_rad={lfc.total_radiation:.0f} W/m²")
    T.ok(f"红蓝比={lfc.red_blue_ratio:.1f}, 光质={lfc.light_quality:.1f}")
    T.ok(f"to_dict 返回 {len(lfc.to_dict())} 字段")

    shaded = LightFieldComponent(in_shadow=True, shadow_intensity=0.8, par=50.0)
    T.ok(f"阴影中: PAR={shaded.par:.0f}, intensity={shaded.shadow_intensity:.0%}") \
        if shaded.in_shadow else T.fail("阴影设置异常")


def test_light_receiver_component():
    """LightReceiverComponent — 光照接收"""
    print("\n[Component] 光照接收组件测试")
    from environment.light_field.components.light_receiver_component import LightReceiverComponent

    lrc = LightReceiverComponent()
    T.ok(f"默认: received={lrc.received_total:.1f}, albedo={lrc.albedo:.1f}")
    T.ok(f"to_dict: {lrc.to_dict()}")

    full = LightReceiverComponent(received_direct=800, received_diffuse=200,
                                   received_total=1000, shade_ratio=0.0)
    T.ok(f"全光照: direct={full.received_direct}, total={full.received_total}") \
        if full.received_total == 1000 else T.fail("光照接收值异常")


# ---------------------------------------------
# 大气组件
# ---------------------------------------------


def test_atmosphere_component():
    """AtmosphereComponent — 创建、海拔效应、空气密度"""
    print("\n[Component] 大气组件测试")
    from environment.atmosphere.components.atmosphere_component import AtmosphereComponent

    atm = AtmosphereComponent()
    T.ok(f"默认: T={atm.temperature}°C, P={atm.pressure:.2f}hPa, "
         f"altitude={atm.altitude}m, air_density={atm.air_density:.4f} kg/m³")
    T.ok(f"气体: O2={atm.oxygen_ratio:.1%}, CO2={atm.co2_ratio:.4%}")
    T.ok(f"湿度系统: RH={atm.humidity:.0%}, vapor={atm.water_vapor}")

    high = AtmosphereComponent(altitude=3000)
    T.ok(f"海拔3000m: P={high.pressure:.2f}hPa, density={high.air_density:.4f} kg/m³")
    T.ok(f"高海拔气压 < 海平面") if high.pressure < atm.pressure else T.fail("高海拔气压应更低")
    T.ok(f"高海拔密度 < 海平面") if high.air_density < atm.air_density else T.fail("高海拔密度应更低")

    hot = AtmosphereComponent(temperature=40)
    T.ok(f"40°C: density={hot.air_density:.4f} kg/m³ < 常温") \
        if hot.air_density < atm.air_density else T.fail("高温应降低密度")


# ---------------------------------------------
# 极端天气事件组件
# ---------------------------------------------


def test_weather_event_components():
    """PhysicalAnomalyComponent — 物理异常检测组件"""
    print("\n[Component] 物理异常事件组件测试")
    from environment.physics_weather.components.weather_event_components import (
        PhysicalAnomalyComponent,
        AnomalySpatialComponent,
        AnomalyStatisticsComponent,
    )

    # 物理异常组件
    anomaly = PhysicalAnomalyComponent(
        anomaly_id=1, variable="temperature",
        current_value=40.0, baseline_value=25.0, baseline_std=5.0,
        deviation_sigma=3.0, duration_hours=6.0, severity=0.8
    )
    T.ok(f"异常: {anomaly.label}, severity={anomaly.severity:.1f}, active={anomaly.is_active}")
    T.ok("异常处于活动状态") if anomaly.is_active else T.fail("异常应处于活动状态")
    T.ok("标签正确") if anomaly.label == "temperature_high" else T.fail("标签异常")

    # 空间组件
    spatial = AnomalySpatialComponent(anomaly_id=1, center_x=50.0, center_y=50.0, radius_km=10.0)
    T.ok(f"空间: center=({spatial.center_x}, {spatial.center_y}), radius={spatial.radius_km}km")

    # 统计组件
    stats = AnomalyStatisticsComponent(anomaly_id=1, max_value=42.0, min_value=38.0, peak_severity=0.9)
    T.ok(f"统计: max={stats.max_value}, min={stats.min_value}, peak={stats.peak_severity}")

    # 非活跃异常
    inactive = PhysicalAnomalyComponent(anomaly_id=2, variable="pressure", deviation_sigma=0.0)
    T.ok("非活跃异常") if not inactive.is_active else T.fail("deviation=0 应不活跃")


# ---------------------------------------------
# 土壤质量与肥力
# ---------------------------------------------


def test_soil_quality_and_fertility():
    """SoilQualityComponent + SoilFertilityComponent + SoilFertilitySystem"""
    print("\n[Component] 土壤质量与肥力测试")
    from environment.soil.components.soil_quality_component import SoilQualityComponent
    from environment.soil.components.soil_fertility_component import SoilFertilityComponent
    from environment.soil.systems.soil_fertility_system import SoilFertilitySystem

    sq = SoilQualityComponent()
    T.ok(f"土壤质量: {sq.quality:.1f}") if 0 < sq.quality <= 1 else T.fail("质量应在 (0,1]")

    sf = SoilFertilityComponent()
    T.ok(f"默认肥力: {sf.fertility:.2f}") if 0 < sf.fertility <= 1 else T.fail("肥力应在 (0,1]")

    world = build_test_world()
    world._world_entity.add_component(SoilFertilityComponent())
    fsystem = SoilFertilitySystem()
    sf_comp = world._world_entity.get_component(SoilFertilityComponent)
    before = sf_comp.fertility
    for _ in range(100):
        fsystem.update(world, 24.0)
    T.ok(f"100天后肥力 {sf_comp.fertility:.5f} > {before:.5f}") \
        if sf_comp.fertility > before else T.fail("肥力应自然恢复")
    T.ok(f"肥力 ≤ 1.0") if sf_comp.fertility <= 1.0 else T.fail("肥力超过上限")


# ---------------------------------------------
# 序列化往返
# ---------------------------------------------


def test_serialization_roundtrip():
    """组件序列化 → to_dict → re-construct"""
    print("\n[Component] 组件序列化往返测试")
    from environment.environment_component import EnvironmentComponent
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.soil.components.soil_component import SoilComponent, SoilType

    orig = EnvironmentComponent(par=500, air_temperature=30, soil_moisture=0.7,
                                 air_humidity=0.8, co2=800)
    d = orig.snapshot()
    restored = EnvironmentComponent(**{k: v for k, v in d.items()
                                        if k in EnvironmentComponent.__dataclass_fields__})
    T.ok(f"EnvironmentComponent: PAR={restored.par}, T={restored.air_temperature}°C") \
        if restored.par == 500 else T.fail("序列化 PAR 不一致")

    pwc = PhysicalWeatherComponent(temperature=35, pressure=1000, wind_speed=10)
    d2 = pwc.to_dict()
    T.ok(f"PWC to_dict: {len(d2)} fields, T={d2['temperature']}°C")

    sc = SoilComponent(soil_type=SoilType.CLAY, moisture=0.6, ph=5.5)
    d3 = sc.to_dict()
    T.ok(f"SoilComponent to_dict: {len(d3)} fields, pH={sc.ph}")


# ---------------------------------------------
# 模块入口
# ---------------------------------------------


def run():
    test_environment_component()
    test_physical_weather_component()
    test_season_component()
    test_climate_component()
    test_light_components()
    test_soil_components()
    test_terrain_component()
    test_light_field_component()
    test_light_receiver_component()
    test_atmosphere_component()
    test_weather_event_components()
    test_soil_quality_and_fertility()
    test_serialization_roundtrip()


if __name__ == "__main__":
    run()
