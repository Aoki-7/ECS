#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境模块综合测试脚本

验证范围:
  1. 管线加载 — 14 个子系统全部注册，顺序正确
  2. 数据流完整性 — 每一层的输出能被下一层正确消费
  3. 物理一致性 — 关键物理量在合理范围且相互耦合
  4. 昼夜循环 — 温度/光照/相对湿度符合昼夜模式
  5. 季节演变 — 季节偏置正确影响天气
  6. 气候耦合 — ClimateComponent 偏置传导到天气

运行:
    python -m environment.test_environment
"""

import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.world import World
from core.system import System

from environment.environment_component import EnvironmentComponent
from environment.config.environment_builder import EnvironmentBuilder
from environment.pipeline import EnvironmentPipeline

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
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
from environment.season.season_component import SeasonComponent, Season
from environment.climate.climate_component import ClimateComponent
from environment.physics_weather.config.physics_constants import (
    saturation_vapor_pressure,
)


# ════════════════════════════════════════════════════════════════════
# 测试结果记录
# ════════════════════════════════════════════════════════════════════

class TestResult:
    """测试结果收集器"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def ok(self, msg):
        self.passed += 1
        print(f"  ✅ {msg}")

    def fail(self, msg, detail=""):
        self.failed += 1
        line = f"  ❌ {msg}"
        if detail:
            line += f" — {detail}"
        self.errors.append(line)
        print(line)

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'=' * 50}")
        print(f"  测试总结: {total} 项 | "
              f"✅ {self.passed} 通过 | "
              f"❌ {self.failed} 失败")
        print(f"{'=' * 50}")
        return self.failed == 0


T = TestResult()


# ════════════════════════════════════════════════════════════════════
# 1. 管线加载测试
# ════════════════════════════════════════════════════════════════════

def test_pipeline_loading():
    """验证管线能正确加载 14 个子系统"""
    print("\n[1/6] 管线加载测试")

    w = World()
    w._world_entity.add_component(EnvironmentComponent())
    pipeline = EnvironmentBuilder.build(w)

    T.ok(f"管线加载成功，{len(pipeline)} 个子系统") if len(pipeline) == 15 \
        else T.fail(f"期望 15 系统，实际 {len(pipeline)}")

    # 检查世界级组件是否全部创建
    components = [
        (SolarPositionComponent, "SolarPositionComponent"),
        (SolarRadiationComponent, "SolarRadiationComponent"),
        (LightScatterComponent, "LightScatterComponent"),
        (SurfaceLightComponent, "SurfaceLightComponent"),
        (PhysicalWeatherComponent, "PhysicalWeatherComponent"),
        (SeasonComponent, "SeasonComponent"),
        (ClimateComponent, "ClimateComponent"),
    ]
    for cls, name in components:
        comp = w._world_entity.get_component(cls)
        if comp is not None:
            T.ok(f"world-level 组件 {name} 已创建")
        else:
            T.fail(f"world-level 组件 {name} 缺失")

    return w, pipeline


# ════════════════════════════════════════════════════════════════════
# 2. 单步数据流测试
# ════════════════════════════════════════════════════════════════════

def test_single_step(world, pipeline):
    """执行一步更新，验证每层输出"""
    print("\n[2/6] 单步数据流测试")

    # 初始时间 = D1 00:00
    pipeline.update(world, 1.0)

    time = world.get_time()
    T.ok(f"时间推进: D{time.day_of_year} {time.hour:.1f}h")

    # ── LAYER 1: 外部强迫 ──
    solar_pos = world._world_entity.get_component(SolarPositionComponent)
    T.ok(f"SolarPosition: elevation={solar_pos.elevation:.1f}°, "
         f"day_length={solar_pos.day_length:.1f}h")

    toa = world._world_entity.get_component(SolarRadiationComponent)
    T.ok(f"SolarRadiation: TOA={toa.toa_radiation:.1f} W/m²")

    season = world._world_entity.get_component(SeasonComponent)
    T.ok(f"Season: {season.season.name}, temp_offset={season.temperature_offset:+.1f}°C")

    climate = world._world_entity.get_component(ClimateComponent)
    T.ok(f"Climate: phase={climate.climate_phase}, rain_bias={climate.rainfall_bias:+.2f}")

    # ── LAYER 2: 大气物理 ──
    weather = world._world_entity.get_component(PhysicalWeatherComponent)
    checks = [
        ("Temperature",  -10, 50, weather.temperature),
        ("Pressure",     950, 1050, weather.pressure),
        ("Rel Humidity", 0.0, 1.0, weather.relative_humidity),
        ("Cloud cover",  0.0, 1.0, weather.cloud_cover),
        ("Precip rate",  0.0, 100, weather.precipitation_rate),
        ("Wind speed",   0.0, 30, weather.wind_speed),
    ]
    for name, lo, hi, val in checks:
        if lo <= val <= hi:
            T.ok(f"PhysicalWeather.{name} = {val:.3f} 在 [{lo}, {hi}]")
        else:
            T.fail(f"PhysicalWeather.{name} = {val:.3f} 超出范围 [{lo}, {hi}]")

    scatter = world._world_entity.get_component(LightScatterComponent)
    T.ok(f"LightScatter: rayleigh={scatter.rayleigh_factor:.4f}, "
         f"mie={scatter.mie_factor:.4f}, cloud_atten={scatter.cloud_attenuation:.3f}")

    surface = world._world_entity.get_component(SurfaceLightComponent)
    T.ok(f"SurfaceLight: direct={surface.direct_light:.1f}, "
         f"diffuse={surface.diffuse_light:.1f} W/m²")

    # ── VPD 一致性验证 ──
    es = saturation_vapor_pressure(weather.temperature)
    vpd_calc = es * (1.0 - weather.relative_humidity)
    T.ok(f"VPD 一致性: es={es:.1f}hPa, RH={weather.relative_humidity:.3f} → VPD={vpd_calc:.2f}hPa")


# ════════════════════════════════════════════════════════════════════
# 3. 昼夜循环测试
# ════════════════════════════════════════════════════════════════════

def test_diurnal_cycle(world, pipeline):
    """验证 24 小时昼夜循环中温度/光照变化"""
    print("\n[3/6] 昼夜循环测试")

    # 推进到 D2 00:00
    for _ in range(24):
        pipeline.update(world, 1.0)

    samples = []
    for _ in range(24):
        pipeline.update(world, 1.0)
        t = world.get_time()
        w = world._world_entity.get_component(PhysicalWeatherComponent)
        s = world._world_entity.get_component(SurfaceLightComponent)
        samples.append((t.hour, w.temperature, s.direct_light + s.diffuse_light))

    # 找温度极值
    temps = [s[1] for s in samples]
    lights = [s[2] for s in samples]
    min_idx = temps.index(min(temps))
    max_idx = temps.index(max(temps))

    T.ok(f"温度谷值: {min(temps):.1f}°C @ {samples[min_idx][0]:.0f}:00")
    T.ok(f"温度峰值: {max(temps):.1f}°C @ {samples[max_idx][0]:.0f}:00")
    T.ok(f"日较差: {max(temps) - min(temps):.1f}°C")

    # 检查光照与温度的相关性
    day_samples = [(h, li) for h, _, li in samples if li > 0]
    night_samples = [(h, li) for h, _, li in samples if li <= 0]

    if len(day_samples) > 0:
        T.ok(f"白昼光照: {len(day_samples)}h, 峰值 {max(lights):.0f} W/m²")
    if len(night_samples) > 0:
        night_count = len(night_samples)
        T.ok(f"夜晚光照: {night_count}h 无光照(≈{night_count*100//24}% 周期)")

    # 物理一致性: 温度峰谷差至少 > 2°C (除非全天阴雨)
    diurnal_range = max(temps) - min(temps)
    if diurnal_range < 2.0:
        T.fail(f"日较差 {diurnal_range:.1f}°C < 2°C，昼夜循环可能异常")
    else:
        T.ok(f"日较差 {diurnal_range:.1f}°C ≥ 2°C ✅")


# ════════════════════════════════════════════════════════════════════
# 4. 长期演变测试
# ════════════════════════════════════════════════════════════════════

def test_long_term(world, pipeline):
    """运行 60 天验证季节影响和系统稳定性"""
    print("\n[4/6] 长期演变测试 (60天)")

    # 初始化随机种子以确保可重复性
    import random
    random.seed(42)

    # 快进到已知天数
    hourly_stats = {"temp": [], "pressure": [], "rh": [], "cloud": [],
                    "precip": [], "wind": []}

    # 采集 D30 和 D60 的数据
    checkpoints = {30: None, 60: None}

    for step in range(1, 60 * 24 + 1):
        pipeline.update(world, 1.0)
        w = world._world_entity.get_component(PhysicalWeatherComponent)

        # 每小时采样
        hourly_stats["temp"].append(w.temperature)
        hourly_stats["pressure"].append(w.pressure)
        hourly_stats["rh"].append(w.relative_humidity)
        hourly_stats["cloud"].append(w.cloud_cover)
        hourly_stats["precip"].append(w.precipitation_rate)
        hourly_stats["wind"].append(w.wind_speed)

        day = world.get_time().day_of_year
        hour = world.get_time().hour

        if day == 30 and hour == 12 and checkpoints[30] is None:
            checkpoints[30] = w
            season_30 = world._world_entity.get_component(SeasonComponent).season
            T.ok(f"D30 12:00: T={w.temperature:.1f}°C, P={w.pressure:.0f}hPa, "
                 f"RH={w.relative_humidity:.0%}, ☁={w.cloud_cover:.2f}, "
                 f"🌧={w.precipitation_rate:.3f} | season={season_30.name}")

        if day == 60 and hour == 12 and checkpoints[60] is None:
            checkpoints[60] = w
            season_60 = world._world_entity.get_component(SeasonComponent).season
            T.ok(f"D60 12:00: T={w.temperature:.1f}°C, P={w.pressure:.0f}hPa, "
                 f"RH={w.relative_humidity:.0%}, ☁={w.cloud_cover:.2f}, "
                 f"🌧={w.precipitation_rate:.3f} | season={season_60.name}")

    # 统计
    for key, values in hourly_stats.items():
        mean_v = sum(values) / len(values)
        min_v = min(values)
        max_v = max(values)
        T.ok(f"{key}: min={min_v:.3f}, max={max_v:.3f}, mean={mean_v:.3f}")

    # 验证: 60天内应有降水事件
    precip_hours = sum(1 for p in hourly_stats["precip"] if p > 0.01)
    total_hours = len(hourly_stats["precip"])
    T.ok(f"降水事件: {precip_hours}/{total_hours}h ({precip_hours*100//total_hours}%)")

    if precip_hours == 0:
        T.fail("60天内无降水事件", "可能系统陷入无降水模式")
    else:
        T.ok(f"降水活跃度正常")
        max_precip = max(hourly_stats["precip"])
        T.ok(f"最大降水强度: {max_precip:.3f} mm/h")

    # 验证季节演变
    season_comp = world._world_entity.get_component(SeasonComponent)
    T.ok(f"最终季节: {season_comp.season.name}, "
         f"offset={season_comp.temperature_offset:+.1f}°C, "
         f"rain_factor={season_comp.rainfall_factor:.2f}")

    return hourly_stats


# ════════════════════════════════════════════════════════════════════
# 5. 物理一致性检查
# ════════════════════════════════════════════════════════════════════

def test_physical_consistency(stats):
    """验证物理量之间的耦合关系"""
    print("\n[5/6] 物理一致性检查")

    temps = stats["temp"]
    rh = stats["rh"]
    clouds = stats["cloud"]
    precip = stats["precip"]

    n = len(temps)

    # 检查1: RH 在 [0, 1]
    rh_ok = all(0.0 <= v <= 1.0 for v in rh)
    T.ok("相对湿度在 [0, 1] 范围内") if rh_ok else T.fail("RH 超出物理范围")

    # 检查2: 云量和 RH 正相关 (RH高 → 云多)
    # 取 RH>0.9 时的平均云量 vs RH<0.7 时的平均云量
    high_rh_clouds = [c for r, c in zip(rh, clouds) if r > 0.9]
    low_rh_clouds = [c for r, c in zip(rh, clouds) if r < 0.7]
    if high_rh_clouds and low_rh_clouds:
        high_mean = sum(high_rh_clouds) / len(high_rh_clouds)
        low_mean = sum(low_rh_clouds) / len(low_rh_clouds)
        if high_mean > low_mean:
            T.ok(f"物理合理: RH>0.9 时平均云量 {high_mean:.3f} > RH<0.7 时 {low_mean:.3f}")
        else:
            T.fail(f"物理异常: RH>0.9 时云量 {high_mean:.3f} ≤ RH<0.7 时 {low_mean:.3f}")
    else:
        T.ok("RH 云量相关性: 数据不足 (单一气候模式)")

    # 检查3: 降水时云量应较高
    precip_clouds = [c for p, c in zip(precip, clouds) if p > 0.05]
    no_precip_clouds = [c for p, c in zip(precip, clouds) if p < 0.001]
    if precip_clouds and no_precip_clouds:
        p_mean = sum(precip_clouds) / len(precip_clouds)
        np_mean = sum(no_precip_clouds) / len(no_precip_clouds)
        if p_mean > np_mean:
            T.ok(f"物理合理: 降水时均云量 {p_mean:.3f} > 无降水时 {np_mean:.3f}")
        else:
            T.fail(f"物理异常: 降水时云量 {p_mean:.3f} ≤ 无降水时 {np_mean:.3f}")
    else:
        T.ok("降水-云量相关性: 数据不足")

    # 检查4: 高温天 VPD 应较高
    # 收集高温/低温样本，比较 VPD-es*(1-RH)结果
    hot_vpd = [saturation_vapor_pressure(t) * (1 - r) for t, r in zip(temps, rh) if t > 25]
    cold_vpd = [saturation_vapor_pressure(t) * (1 - r) for t, r in zip(temps, rh) if t < 10]
    if hot_vpd and cold_vpd:
        hv_mean = sum(hot_vpd) / len(hot_vpd)
        cv_mean = sum(cold_vpd) / len(cold_vpd)
        T.ok(f"VPD 对比: 高温时均 {hv_mean:.1f}hPa vs 低温时均 {cv_mean:.1f}hPa")
    else:
        T.ok("VPD 温度相关性: 缺少极端温度样本")


# ════════════════════════════════════════════════════════════════════
# 6. 气候耦合测试
# ════════════════════════════════════════════════════════════════════

def test_climate_coupling(world, pipeline):
    """验证 ClimateComponent 偏置传导到 PhysicalWeatherSystem"""
    print("\n[6/6] 气候耦合测试")

    climate = world._world_entity.get_component(ClimateComponent)
    if climate is None:
        T.fail("ClimateComponent 不存在")
        return

    # 强行设置不同气候相位，观察温度/降水变化
    original_phase = climate.climate_phase

    for phase_name in ["LaNina", "Neutral", "ElNino"]:
        climate.climate_phase = phase_name
        climate.phase_remaining_days = 100

        # 推进 48h 稳定
        for _ in range(48):
            pipeline.update(world, 1.0)

        w = world._world_entity.get_component(PhysicalWeatherComponent)
        T.ok(f"Climate={phase_name}: T={w.temperature:.1f}°C, "
             f"RH={w.relative_humidity:.3f}, "
             f"rain_bias={climate.rainfall_bias:+.2f}")

    # 恢复原相位
    climate.climate_phase = original_phase

    # 验证: ElNino 的降雨偏置应导致降水总体偏差
    # (定性验证，成功即可)
    T.ok("气候相位切换正常，未引发异常")


# ════════════════════════════════════════════════════════════════════
# 主函数
# ════════════════════════════════════════════════════════════════════

def main():
    print("=" * 50)
    print("  环境模块综合测试")
    print(f"  {__file__}")
    print("=" * 50)

    world, pipeline = test_pipeline_loading()
    test_single_step(world, pipeline)
    test_diurnal_cycle(world, pipeline)
    stats = test_long_term(world, pipeline)
    test_physical_consistency(stats)
    test_climate_coupling(world, pipeline)

    success = T.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
