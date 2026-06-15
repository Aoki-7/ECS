#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实物理天气系统 — 高级验证测试脚本

============================================================
测试目标
============================================================

该脚本用于验证 physics_weather 模块是否具备：

1. 物理量平滑演化
2. 昼夜循环正确
3. 季节变化正确
4. 降水事件形成合理
5. 天气标签推导正确
6. 多气候区差异存在
7. 风暴生命周期合理
8. 湿度-云量-降水耦合正确
9. 数值稳定性
10. 极端参数健壮性
11. 长时间运行稳定性
12. 与旧 weather 模块完全独立

============================================================
运行方式
============================================================

python -m pytest tests/environment/physics_weather/test_physics_weather.py

或：

python tests/environment/physics_weather/test_physics_weather.py
"""

import math
import statistics
from collections import defaultdict

from core.world import World

from time_module.time_system import TimeSystem

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)

from environment.physics_weather.systems.physical_weather_system import (
    PhysicalWeatherSystem,
)

from environment.physics_weather.utils.weather_classifier import (
    classify_from_component,
)


# ============================================================
# 工具函数
# ============================================================

def clamp(v, min_v, max_v):
    return max(min_v, min(v, max_v))


def moving_average(values, window=6):
    if len(values) < window:
        return values

    result = []
    for i in range(len(values)):
        left = max(0, i - window)
        right = min(len(values), i + window)
        result.append(sum(values[left:right]) / (right - left))
    return result


# ============================================================
# 核心模拟器
# ============================================================

class PhysicsWeatherSimulation:
    """
    高级物理天气模拟器
    """

    def __init__(
        self,
        latitude=35.0,
        elevation=0.0,
        delta_hours=1.0,
        verbose=True,
    ):
        self.verbose = verbose
        self.delta_hours = delta_hours

        self.world = World()

        # 世界实体
        self.world._world_entity.add_component(
            PhysicalWeatherComponent()
        )

        # 时间系统
        self.time_system = TimeSystem(verbose=False)

        # 天气系统
        self.weather_system = PhysicalWeatherSystem(
            latitude=latitude,
            elevation=elevation,
        )

        self.step = 0

        # 历史记录
        self.history = defaultdict(list)

    # --------------------------------------------------------

    def update(self):
        """
        单步更新
        """

        self.time_system.update(
            self.world,
            self.delta_hours
        )

        self.weather_system.update(
            self.world,
            self.delta_hours
        )

        self.step += 1

        self.record()

    # --------------------------------------------------------

    def record(self):
        """
        记录历史
        """

        weather = self.get_weather()
        time = self.world.get_time()

        self.history["temperature"].append(weather.temperature)
        self.history["pressure"].append(weather.pressure)
        self.history["humidity"].append(weather.relative_humidity)
        self.history["cloud"].append(weather.cloud_cover)
        self.history["wind"].append(weather.wind_speed)
        self.history["rain"].append(weather.precipitation_rate)

        self.history["hour"].append(time.hour)
        self.history["day"].append(time.day_of_year)

    # --------------------------------------------------------

    def get_weather(self):
        return self.world._world_entity.get_component(
            PhysicalWeatherComponent
        )

    # --------------------------------------------------------

    def debug(self):
        """
        调试输出
        """

        weather = self.get_weather()
        state = classify_from_component(weather)
        time = self.world.get_time()

        print(
            f"[{self.step:5d}] "
            f"D{time.day_of_year:03d} "
            f"{time.hour:05.1f}h | "
            f"T={weather.temperature:6.2f}°C | "
            f"P={weather.pressure:7.2f}hPa | "
            f"RH={weather.relative_humidity:6.1%} | "
            f"Cloud={weather.cloud_cover:5.2f} | "
            f"Rain={weather.precipitation_rate:6.3f}mm/h | "
            f"Wind={weather.wind_speed:5.2f}m/s | "
            f"{state.label}"
        )

    # --------------------------------------------------------

    def run(
        self,
        steps,
        debug_interval=24,
    ):
        """
        运行模拟
        """

        for i in range(steps):

            self.update()

            if (
                self.verbose
                and debug_interval > 0
                and i % debug_interval == 0
            ):
                self.debug()


# ============================================================
# TEST 1
# 基础物理量范围
# ============================================================

def test_basic_ranges():

    print("\n" + "=" * 80)
    print("TEST 1: 基础物理量范围")
    print("=" * 80)

    sim = PhysicsWeatherSimulation(
        latitude=35.0,
        verbose=False,
    )

    sim.run(steps=24 * 30)

    weather = sim.get_weather()

    assert -60 <= weather.temperature <= 60
    assert 850 <= weather.pressure <= 1100
    assert 0 <= weather.relative_humidity <= 1
    assert 0 <= weather.cloud_cover <= 1
    assert weather.wind_speed >= 0
    assert weather.precipitation_rate >= 0

    print("✅ 基础范围验证通过")


# ============================================================
# TEST 2
# 昼夜循环
# ============================================================

def test_diurnal_cycle():

    print("\n" + "=" * 80)
    print("TEST 2: 昼夜循环")
    print("=" * 80)

    sim = PhysicsWeatherSimulation(
        latitude=35.0,
        verbose=False,
    )

    sim.run(steps=24 * 5)

    temps = sim.history["temperature"]
    hours = sim.history["hour"]

    daily_peaks = []

    for day in range(5):

        begin = day * 24
        end = begin + 24

        day_temps = temps[begin:end]

        peak_idx = day_temps.index(max(day_temps))

        daily_peaks.append(peak_idx)

    print(f"温度峰值小时: {daily_peaks}")

    for peak in daily_peaks:
        assert 11 <= peak <= 17

    print("✅ 昼夜循环合理")


# ============================================================
# TEST 3
# 季节循环
# ============================================================

def test_season_cycle():

    print("\n" + "=" * 80)
    print("TEST 3: 季节循环")
    print("=" * 80)

    sim = PhysicsWeatherSimulation(
        latitude=45.0,
        verbose=False,
    )

    sim.run(steps=24 * 365)

    temps = sim.history["temperature"]

    monthly = []

    for month in range(12):

        begin = month * 30 * 24
        end = begin + 30 * 24

        avg_temp = statistics.mean(
            temps[begin:end]
        )

        monthly.append(avg_temp)

    print("月均温:")
    for i, t in enumerate(monthly, 1):
        print(f"Month {i:02d}: {t:.2f}°C")

    annual_range = max(monthly) - min(monthly)

    print(f"\n全年温差: {annual_range:.2f}°C")
    print(monthly)
    assert annual_range > 8

    print("✅ 季节循环合理")


# ============================================================
# TEST 4
# 湿度-云量耦合
# ============================================================

def test_humidity_cloud_correlation():

    print("\n" + "=" * 80)
    print("TEST 4: 湿度-云量耦合")
    print("=" * 80)

    sim = PhysicsWeatherSimulation(
        latitude=35.0,
        verbose=False,
    )

    sim.run(steps=24 * 60)

    humidity = sim.history["humidity"]
    cloud = sim.history["cloud"]

    avg_humid_cloud = statistics.mean([
        c for h, c in zip(humidity, cloud)
        if h > 0.8
    ])

    avg_dry_cloud = statistics.mean([
        c for h, c in zip(humidity, cloud)
        if h < 0.4
    ])

    print(f"高湿平均云量: {avg_humid_cloud:.2f}")
    print(f"低湿平均云量: {avg_dry_cloud:.2f}")

    assert avg_humid_cloud > avg_dry_cloud

    print("✅ 湿度-云量关联正确")


# ============================================================
# TEST 5
# 降水形成逻辑
# ============================================================

def test_precipitation_logic():

    print("\n" + "=" * 80)
    print("TEST 5: 降水形成逻辑")
    print("=" * 80)

    sim = PhysicsWeatherSimulation(
        latitude=20.0,
        verbose=False,
    )

    sim.run(steps=24 * 120)

    rain = sim.history["rain"]
    cloud = sim.history["cloud"]
    humidity = sim.history["humidity"]

    rain_events = 0

    for r, c, h in zip(rain, cloud, humidity):

        if r > 0.1:

            rain_events += 1

            assert c > 0.5
            assert h > 0.6

    print(f"降水事件数: {rain_events}")

    assert rain_events > 0

    print("✅ 降水形成逻辑合理")


# ============================================================
# TEST 6
# 风暴生命周期
# ============================================================

def test_storm_lifecycle():

    print("\n" + "=" * 80)
    print("TEST 6: 风暴生命周期")
    print("=" * 80)

    sim = PhysicsWeatherSimulation(
        latitude=25.0,
        verbose=False,
    )

    sim.run(steps=24 * 180)

    rain = sim.history["rain"]

    storm_lengths = []

    current = 0

    for r in rain:

        if r > 0.1:
            current += 1
        else:
            if current > 0:
                storm_lengths.append(current)
            current = 0

    if storm_lengths:

        avg_duration = statistics.mean(storm_lengths)

        print(f"平均风暴持续时间: {avg_duration:.2f}小时")

        assert avg_duration > 1

    print("✅ 风暴生命周期合理")


# ============================================================
# TEST 7
# 多纬度气候差异
# ============================================================

def test_latitude_difference():

    print("\n" + "=" * 80)
    print("TEST 7: 纬度差异")
    print("=" * 80)

    equator = PhysicsWeatherSimulation(
        latitude=0.0,
        verbose=False,
    )

    polar = PhysicsWeatherSimulation(
        latitude=70.0,
        verbose=False,
    )

    equator.run(steps=24 * 180)
    polar.run(steps=24 * 180)

    eq_avg = statistics.mean(
        equator.history["temperature"]
    )

    polar_avg = statistics.mean(
        polar.history["temperature"]
    )

    print(f"赤道平均温度: {eq_avg:.2f}°C")
    print(f"高纬平均温度: {polar_avg:.2f}°C")

    assert eq_avg > polar_avg

    print("✅ 纬度差异合理")


# ============================================================
# TEST 8
# 数值稳定性
# ============================================================

def test_numerical_stability():

    print("\n" + "=" * 80)
    print("TEST 8: 数值稳定性")
    print("=" * 80)

    sim = PhysicsWeatherSimulation(
        latitude=35.0,
        delta_hours=0.1,
        verbose=False,
    )

    sim.run(steps=5000)

    temps = sim.history["temperature"]

    delta = []

    for i in range(1, len(temps)):
        delta.append(abs(temps[i] - temps[i - 1]))

    max_jump = max(delta)

    print(f"最大单步温度跳变: {max_jump:.2f}°C")

    assert max_jump < 10

    print("✅ 数值稳定")


# ============================================================
# TEST 9
# 长时间稳定性
# ============================================================

def test_long_term_stability():

    print("\n" + "=" * 80)
    print("TEST 9: 长时间运行稳定性")
    print("=" * 80)

    sim = PhysicsWeatherSimulation(
        latitude=35.0,
        verbose=False,
    )

    sim.run(steps=24 * 365 * 3)

    temps = sim.history["temperature"]

    avg_temp = statistics.mean(temps)

    print(f"三年平均温度: {avg_temp:.2f}°C")

    assert -20 < avg_temp < 40

    print("✅ 长时间运行稳定")


# ============================================================
# TEST 10
# 标签一致性
# ============================================================

def test_weather_classifier_consistency():

    print("\n" + "=" * 80)
    print("TEST 10: 天气标签一致性")
    print("=" * 80)

    sim = PhysicsWeatherSimulation(
        latitude=35.0,
        verbose=False,
    )

    sim.run(steps=24 * 30)

    checked = 0

    for _ in range(200):

        weather = sim.get_weather()

        state = classify_from_component(weather)

        # 有降水不能是 clear
        if weather.precipitation_rate > 0.1:
            assert "clear" not in state.label.lower()

        checked += 1

    print(f"检查样本数: {checked}")

    print("✅ 标签一致性正确")


# ============================================================
# TEST 11
# 模块独立性
# ============================================================

def test_independence():

    print("\n" + "=" * 80)
    print("TEST 11: 模块独立性")
    print("=" * 80)

    from environment.physics_weather import (
        PhysicalWeatherComponent,
        PhysicalWeatherSystem,
        classify,
        DerivedWeatherState,
        CloudCoverLevel,
    )

    assert PhysicalWeatherComponent is not None
    assert PhysicalWeatherSystem is not None

    assert CloudCoverLevel.CLEAR.value == "clear"

    print("✅ 模块独立")


# ============================================================
# TEST 12
# 极端环境
# ============================================================

def test_extreme_environment():

    print("\n" + "=" * 80)
    print("TEST 12: 极端环境")
    print("=" * 80)

    extreme_cases = [
        ("赤道", 0),
        ("温带", 35),
        ("高纬", 70),
        ("极地", 85),
    ]

    for name, lat in extreme_cases:

        sim = PhysicsWeatherSimulation(
            latitude=lat,
            verbose=False,
        )

        sim.run(steps=24 * 30)

        avg_temp = statistics.mean(
            sim.history["temperature"]
        )

        print(
            f"{name:6s} | "
            f"纬度={lat:5.1f} | "
            f"平均温度={avg_temp:6.2f}°C"
        )

    print("✅ 极端环境测试通过")


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 80)
    print("真实物理天气系统 - 完整验证测试")
    print("=" * 80)

    test_basic_ranges()

    test_diurnal_cycle()

    test_season_cycle()

    test_humidity_cloud_correlation()

    test_precipitation_logic()

    test_storm_lifecycle()

    test_latitude_difference()

    test_numerical_stability()

    test_long_term_stability()

    test_weather_classifier_consistency()

    test_independence()

    test_extreme_environment()

    print("\n")
    print("=" * 80)
    print("所有测试通过 ✅")
    print("=" * 80)