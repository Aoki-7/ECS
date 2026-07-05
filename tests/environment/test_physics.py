#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物理常量、天气分类器、VPD、边界条件与数据完整性测试
"""

import math

from environment.systems.environment_sync_system import EnvironmentSyncSystem
from tests.environment.base import T, build_test_world, setup_weather_world


# ════════════════════════════════════════════════════════════
# 物理常量与辅助函数
# ════════════════════════════════════════════════════════════


def test_physics_constants():
    """物理常量与辅助函数"""
    print("\n[Physics] 物理常量与辅助函数测试")
    from environment.physics_weather.config.physics_constants import (
        saturation_vapor_pressure,
        saturation_absolute_humidity,
        relative_humidity,
    )

    es_0 = saturation_vapor_pressure(0)
    T.ok(f"0°C 饱和水汽压 = {es_0:.3f} hPa (≈6.11)") if 5.0 < es_0 < 7.0 else T.fail(f"饱和水汽压异常: {es_0}")

    es_25 = saturation_vapor_pressure(25)
    T.ok(f"25°C 饱和水汽压 = {es_25:.3f} hPa (≈31.7)") if 30.0 < es_25 < 33.0 else T.fail(f"25°C 饱和水汽压异常: {es_25}")

    ah_25 = saturation_absolute_humidity(25)
    T.ok(f"25°C 饱和绝对湿度 = {ah_25:.3f} g/m³ (≈23)") if 20 < ah_25 < 26 else T.fail(f"25°C 饱和绝湿异常: {ah_25}")

    rh = relative_humidity(5.0, 25.0)
    T.ok(f"AH=5, T=25 → RH={rh:.3f} (≈0.21)") if 0.15 < rh < 0.30 else T.fail(f"RH 计算异常: {rh}")

    rh_0 = relative_humidity(0, 25)
    T.ok(f"AH=0 → RH={rh_0}") if rh_0 == 0.0 else T.fail("AH=0 时 RH 应为 0")

    ah_sat = saturation_absolute_humidity(25)
    rh_sat = relative_humidity(ah_sat, 25)
    T.ok(f"饱和时 RH={rh_sat:.4f} (≈1.0)") if abs(rh_sat - 1.0) < 0.01 else T.fail(f"饱和 RH 计算异常: {rh_sat}")


# ════════════════════════════════════════════════════════════
# 天气分类器
# ════════════════════════════════════════════════════════════


def test_weather_classifier_cloud_cover():
    """WeatherClassifier.cloud_cover — 全云量范围"""
    print("\n[Physics] 天气分类器 — 云量等级")
    from environment.physics_weather.utils.weather_classifier import classify_cloud_cover
    from environment.physics_weather.config.weather_thresholds import CloudCoverLevel

    cases = [
        (0.0, CloudCoverLevel.CLEAR),
        (0.03, CloudCoverLevel.CLEAR),
        (0.1, CloudCoverLevel.PARTLY_CLOUDY),
        (0.3, CloudCoverLevel.CLOUDY),
        (0.6, CloudCoverLevel.OVERCAST),
        (1.0, CloudCoverLevel.OVERCAST),
    ]
    for val, expected in cases:
        actual = classify_cloud_cover(val)
        ok = actual == expected
        T.ok(f"cloud={val:.2f} → {actual.value}") if ok else T.fail(f"cloud={val} 应为 {expected.value}, 实际 {actual.value}")


def test_weather_classifier_precipitation():
    """WeatherClassifier.precipitation — 类型 + 强度"""
    print("\n[Physics] 天气分类器 — 降水类型与强度")
    from environment.physics_weather.utils.weather_classifier import (
        classify_precipitation_type, classify_precipitation_intensity,
    )
    from environment.physics_weather.config.weather_thresholds import (
        PrecipitationType, PrecipitationIntensity,
        SNOW_TEMP_THRESHOLD, SLEET_TEMP_UPPER,
    )

    cases_type = [
        (1.0, -5.0, PrecipitationType.SNOW),
        (1.0, 0.0, PrecipitationType.SLEET),
        (1.0, 5.0, PrecipitationType.RAIN),
        (0.0, 25.0, PrecipitationType.NONE),
    ]
    for rate, temp, expected in cases_type:
        actual = classify_precipitation_type(rate, temp)
        T.ok(f"rate={rate}, T={temp}°C → {actual.value}") \
            if actual == expected else T.fail(f"应为 {expected.value}, 实际 {actual.value}")

    cases_intensity = [
        (0.0, PrecipitationIntensity.NONE),
        (0.05, PrecipitationIntensity.LIGHT),
        (1.0, PrecipitationIntensity.MODERATE),
        (5.0, PrecipitationIntensity.HEAVY),
        (20.0, PrecipitationIntensity.EXTREME),
        (100.0, PrecipitationIntensity.EXTREME),
    ]
    for rate, expected in cases_intensity:
        actual = classify_precipitation_intensity(rate)
        T.ok(f"rate={rate} → {actual.value}") \
            if actual == expected else T.fail(f"rate={rate} 应为 {expected.value}, 实际 {actual.value}")

    T.ok(f"雪温阈值 = {SNOW_TEMP_THRESHOLD}°C") if SNOW_TEMP_THRESHOLD == -2.0 else T.fail("雪温阈值异常")
    T.ok(f"雨夹雪上限 = {SLEET_TEMP_UPPER}°C") if SLEET_TEMP_UPPER == 2.0 else T.fail("雨夹雪阈值异常")


def test_weather_classifier_wind_visibility():
    """WeatherClassifier.wind + visibility — 风与能见度"""
    print("\n[Physics] 天气分类器 — 风级与能见度")
    from environment.physics_weather.utils.weather_classifier import (
        classify, classify_from_component, classify_wind_level,
    )
    from environment.physics_weather.config.weather_thresholds import (
        WindLevel, PrecipitationType, FOG_RH_THRESHOLD, DENSE_FOG_RH_THRESHOLD,
    )
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )

    cases = [
        (0.0, WindLevel.CALM),
        (0.2, WindLevel.CALM),
        (3.0, WindLevel.STRONG),
        (8.0, WindLevel.GALE),
        (15.0, WindLevel.STORM),
        (50.0, WindLevel.STORM),
    ]
    for speed, expected in cases:
        actual = classify_wind_level(speed)
        T.ok(f"wind={speed} → {actual.value}") \
            if actual == expected else T.fail(f"wind={speed} 应为 {expected.value}, 实际 {actual.value}")

    T.ok(f"雾阈值 RH>{FOG_RH_THRESHOLD:.0%}, 浓雾 RH>{DENSE_FOG_RH_THRESHOLD:.0%}")

    state = classify(temperature=30, relative_humidity=0.4, cloud_cover=0.2,
                     precipitation_rate=0, wind_speed=2.0)
    T.ok(f"晴天: label='{state.label}', full='{state.full_label}'")
    T.ok(f"label 非空") if state.label else T.fail("分类结果 label 为空")

    storm = classify(temperature=25, relative_humidity=0.95, cloud_cover=0.8,
                     precipitation_rate=15.0, wind_speed=12.0)
    T.ok(f"暴雨: label='{storm.label}', full='{storm.full_label}'")
    T.ok(f"降水类型={storm.precipitation_type.value}") \
        if storm.precipitation_type == PrecipitationType.RAIN else T.fail("暴雨应为雨")

    blizzard = classify(temperature=-10, relative_humidity=0.9, cloud_cover=0.9,
                        precipitation_rate=5.0, wind_speed=15.0)
    T.ok(f"暴雪: label='{blizzard.label}', full='{blizzard.full_label}'")
    T.ok(f"降水类型={blizzard.precipitation_type.value}") \
        if blizzard.precipitation_type == PrecipitationType.SNOW else T.fail("暴雪应为雪")

    pwc = PhysicalWeatherComponent(temperature=20, relative_humidity=0.65,
                                    cloud_cover=0.3, wind_speed=3.0)
    derived = classify_from_component(pwc)
    T.ok(f"from_component: label='{derived.label}'") if derived.label else T.fail("classify_from_component 失败")


# ════════════════════════════════════════════════════════════
# VPD 计算
# ════════════════════════════════════════════════════════════


def test_vpd_calculation():
    """VPD (蒸汽压亏缺) — 从温度+RH推导"""
    print("\n[Physics] VPD 计算验证")
    from environment.physics_weather.config.physics_constants import saturation_vapor_pressure

    es_hot = saturation_vapor_pressure(35.0)
    vpd_hot = es_hot * (1 - 0.3) / 10.0
    T.ok(f"35°C/RH=30%: VPD={vpd_hot:.2f} kPa (高)") if vpd_hot > 2.0 else T.fail("VPD 偏低")

    es_cold = saturation_vapor_pressure(15.0)
    vpd_cold = es_cold * (1 - 0.9) / 10.0
    T.ok(f"15°C/RH=90%: VPD={vpd_cold:.2f} kPa (低)") if vpd_cold < 0.5 else T.fail("VPD 偏高")

    T.ok("VPD ≥ 0") if vpd_hot >= 0 and vpd_cold >= 0 else T.fail("VPD 为负")


# ════════════════════════════════════════════════════════════
# 边界条件与极端场景
# ════════════════════════════════════════════════════════════


def test_extreme_temperature():
    """极端温度 — PhysicalWeatherSystem 不应发散"""
    print("\n[Physics] 极端温度稳定性测试")
    from environment.physics_weather.systems.physical_weather_system import PhysicalWeatherSystem
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from time_module.time_component import TimeComponent

    for extreme_temp in [-30.0, 50.0]:
        world = setup_weather_world(build_test_world())
        weather = world.get_world_component(PhysicalWeatherComponent)
        weather.temperature = extreme_temp

        pws = PhysicalWeatherSystem(latitude=35.0)
        time_comp = world.get_world_component(TimeComponent)
        time_comp.hour = 12.0
        time_comp.day_of_year = 80

        max_change = 0.0
        for _ in range(10):
            before = weather.temperature
            pws.update(world, 1.0)
            after = weather.temperature
            max_change = max(max_change, abs(after - before))

        in_range = -50 <= weather.temperature <= 60
        T.ok(f"起始 {extreme_temp}°C: 10步后 {weather.temperature:.1f}°C, "
             f"最大单步变化 {max_change:.2f}°C, 稳定在合理范围") \
            if in_range else T.fail(f"温度发散: {weather.temperature}°C")


def test_no_precipitation_drought():
    """干旱条件 — 多日无降水时土壤水分持续下降"""
    print("\n[Physics] 干旱条件模拟")
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.soil.components.soil_moisture_component import SoilMoistureComponent
    from environment.soil.systems.soil_water_balance_system import SoilWaterBalanceSystem

    world = build_test_world()
    world.add_component(world._world_entity, PhysicalWeatherComponent())
    world.add_component(world._world_entity, SoilMoistureComponent())

    weather = world.get_world_component(PhysicalWeatherComponent)
    soil = world.get_world_component(SoilMoistureComponent)

    weather.precipitation_rate = 0.0
    weather.temperature = 35.0
    soil.moisture = 0.8
    soil.capacity = 1.0

    swbs = SoilWaterBalanceSystem()
    moisture_trace = [soil.moisture]
    for _ in range(72):
        swbs.update(world, 1.0)
        moisture_trace.append(soil.moisture)

    T.ok(f"干旱3天: 湿度从 {moisture_trace[0]:.3f} 降至 {moisture_trace[-1]:.3f}")
    T.ok(f"湿度持续下降") if moisture_trace[-1] < moisture_trace[0] else T.fail("干旱条件湿度应下降")
    T.ok(f"湿度未跌为负") if moisture_trace[-1] >= 0 else T.fail("湿度小于0")

    weather.precipitation_rate = 10.0
    for _ in range(12):
        swbs.update(world, 1.0)
        moisture_trace.append(soil.moisture)

    T.ok(f"暴雨12h后: 湿度恢复至 {soil.moisture:.3f}")
    T.ok(f"降雨后湿度回升") if soil.moisture > moisture_trace[-13] else T.fail("降雨后湿度下降")


def test_heavy_precipitation_flood():
    """暴雨条件 — 土壤湿度不应超过容量"""
    print("\n[Physics] 暴雨条件模拟")
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.soil.components.soil_moisture_component import SoilMoistureComponent
    from environment.soil.systems.soil_water_balance_system import SoilWaterBalanceSystem

    world = build_test_world()
    world.add_component(world._world_entity, PhysicalWeatherComponent())
    world.add_component(world._world_entity, SoilMoistureComponent())

    weather = world.get_world_component(PhysicalWeatherComponent)
    soil = world.get_world_component(SoilMoistureComponent)

    weather.precipitation_rate = 50.0
    weather.temperature = 20.0
    soil.moisture = 0.3
    soil.capacity = 1.0

    swbs = SoilWaterBalanceSystem()
    for _ in range(48):
        swbs.update(world, 1.0)

    T.ok(f"暴雨2天后: moisture={soil.moisture:.4f} ≤ capacity={soil.capacity}") \
        if soil.moisture <= soil.capacity else T.fail(f"土壤水分超过容量: {soil.moisture} > {soil.capacity}")


def test_nighttime_inversion():
    """夜间逆温 — 凌晨温度谷值验证"""
    print("\n[Physics] 夜间至凌晨温度行为")
    from environment.physics_weather.systems.physical_weather_system import PhysicalWeatherSystem
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from time_module.time_component import TimeComponent

    world = setup_weather_world(build_test_world())
    pws = PhysicalWeatherSystem(latitude=35.0)
    time_comp = world.get_world_component(TimeComponent)
    time_comp.day_of_year = 80
    time_comp.hour = 20.0

    temps = []
    for h in range(12):
        time_comp.hour = (20 + h) % 24
        pws.update(world, 1.0)
        weather = world.get_world_component(PhysicalWeatherComponent)
        temps.append(weather.temperature)

    night_temps = temps[:8]
    if len(night_temps) >= 2:
        T.ok(f"夜间温度变化: {night_temps[0]:.1f}°C → {night_temps[-1]:.1f}°C")
        T.ok(f"凌晨温度 ≤ 傍晚温度") if night_temps[-1] <= night_temps[0] + 0.5 \
            else T.fail(f"夜间温度未下降: {night_temps[0]:.1f} → {night_temps[-1]:.1f}")


# ════════════════════════════════════════════════════════════
# 数据完整性
# ════════════════════════════════════════════════════════════


def test_no_nan_inf():
    """数据完整性 — 所有物理量不含 NaN/Inf"""
    print("\n[Physics] 数据完整性 — 无 NaN/Inf")
    from environment.physics_weather.config.physics_constants import (
        saturation_vapor_pressure, saturation_absolute_humidity, relative_humidity,
    )
    from environment.environment_component import EnvironmentComponent

    consts = [
        ("saturation_vapor_pressure(0)", saturation_vapor_pressure(0)),
        ("saturation_vapor_pressure(50)", saturation_vapor_pressure(50)),
        ("saturation_absolute_humidity(20)", saturation_absolute_humidity(20)),
        ("relative_humidity(5, 25)", relative_humidity(5, 25)),
    ]
    for name, val in consts:
        valid = math.isfinite(val)
        T.ok(f"{name} = {val:.4f}") if valid else T.fail(f"{name} = {val} (不是有限数)")

    data = EnvironmentSyncSystem.snapshot(EnvironmentComponent())
    all_finite = all(
        math.isfinite(v) if isinstance(v, (int, float)) else True
        for v in data.values()
    )
    T.ok("EnvironmentComponent 所有数值字段有限") if all_finite else T.fail("存在 NaN/Inf")


# ════════════════════════════════════════════════════════════
# 运行入口
# ════════════════════════════════════════════════════════════


def run():
    test_physics_constants()
    test_weather_classifier_cloud_cover()
    test_weather_classifier_precipitation()
    test_weather_classifier_wind_visibility()
    test_vpd_calculation()
    test_extreme_temperature()
    test_no_precipitation_drought()
    test_heavy_precipitation_flood()
    test_nighttime_inversion()
    test_no_nan_inf()


if __name__ == "__main__":
    run()
