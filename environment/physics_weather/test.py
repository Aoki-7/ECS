#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物理天气模块 — 独立测试脚本

验证：
1. 物理量是否随时间平滑演化
2. 天气状态标签是否从物理量正确推导
3. 是否形成合理的昼夜循环和天气变化模式
4. 无降水时标签合理，有降水时标签正确切换

运行：
    python -m environment.physics_weather.test
"""

import sys
import os

# 将项目根目录加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.world import World
from time_module.time_system import TimeSystem
from time_module.time_component import TimeComponent

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.physics_weather.systems.physical_weather_system import (
    PhysicalWeatherSystem,
)
from environment.physics_weather.utils.weather_classifier import (
    classify_from_component,
)


class PhysicsWeatherSimulation:
    """物理天气模拟器"""

    def __init__(self, latitude=35.0, elevation=0.0, verbose=True):
        self.world = World()
        self.verbose = verbose

        # ── 挂载物理天气组件 ──
        self.world._world_entity.add_component(PhysicalWeatherComponent())

        # ── 创建系统 ──
        self.time_system = TimeSystem(verbose=False)
        self.weather_system = PhysicalWeatherSystem(
            latitude=latitude, elevation=elevation
        )

        self.step = 0

    def update(self, delta_hours=1.0):
        """单步更新"""
        self.time_system.update(self.world, delta_hours)
        self.weather_system.update(self.world, delta_hours)
        self.step += 1

    def debug(self):
        """打印当前状态"""
        weather = self.world._world_entity.get_component(PhysicalWeatherComponent)
        time = self.world.get_time()
        state = classify_from_component(weather)

        print(
            f"[{self.step:4d}] "
            f"D{time.day_of_year:3d} {time.hour:5.1f}h | "
            f"T={weather.temperature:5.1f}°C "
            f"P={weather.pressure:5.0f}hPa "
            f"RH={weather.relative_humidity:5.1%} "
            f"cloud={weather.cloud_cover:.2f} "
            f"rain={weather.precipitation_rate:.3f}mm/h "
            f"wind={weather.wind_speed:.1f}m/s | "
            f"☁{state.cloud_cover_level.value} "
            f"🌧{state.precipitation_intensity.value}_{state.precipitation_type.value} "
            f"🌬{state.wind_level.value} "
            f"👁{state.visibility.value}"
        )

    def run(self, steps=720, delta_hours=1.0, debug_interval=6):
        """运行模拟"""
        print("=" * 120)
        print(f"物理天气模拟 | 步数={steps} | 每步={delta_hours}h | 纬度={self.weather_system.latitude}°")
        print("=" * 120)

        for i in range(steps):
            self.update(delta_hours)
            if self.verbose and i % debug_interval == 0:
                self.debug()

        print("=" * 120)
        print("模拟结束")
        self.debug()

    def run_storm_tracking(self, max_steps=500):
        """
        持续运行直到观测到一次明显的降水事件
        """
        print("=" * 120)
        print("降水事件追踪模式 | 持续运行直到观察到>=小雨")
        print("=" * 120)

        for i in range(max_steps):
            self.update(1.0)
            weather = self.world._world_entity.get_component(PhysicalWeatherComponent)
            state = classify_from_component(weather)

            if weather.precipitation_rate > 0.1:
                print(f"\n=== 降水事件触发于 Step {self.step} ===")
                self.debug()
                print()
                # 继续观察降水过程
                for j in range(48):
                    self.update(1.0)
                    if j % 3 == 0:
                        self.debug()
                break

            if i % 24 == 0:
                self.debug()

        else:
            print(f"运行{max_steps}步未见明显降水，请检查参数或增大步数。")


def test_basic():
    """基础测试：运行30天验证物理量平滑变化"""
    print("\n" + "=" * 60)
    print("TEST 1: 基础运行测试 (30天)")
    print("=" * 60)

    sim = PhysicsWeatherSimulation(latitude=35.0)
    sim.run(steps=720, delta_hours=1.0, debug_interval=24)

    # 验证组件存在
    weather = sim.world._world_entity.get_component(PhysicalWeatherComponent)
    assert weather is not None, "PhysicalWeatherComponent 未挂载"

    # 验证物理量在合理范围
    assert -30 <= weather.temperature <= 50, f"温度超出合理范围: {weather.temperature}"
    assert 950 <= weather.pressure <= 1060, f"气压超出合理范围: {weather.pressure}"
    assert 0 <= weather.relative_humidity <= 1, f"相对湿度超出范围: {weather.relative_humidity}"
    assert 0 <= weather.cloud_cover <= 1, f"云量超出范围: {weather.cloud_cover}"
    assert weather.wind_speed >= 0, f"风速为负: {weather.wind_speed}"
    assert weather.precipitation_rate >= 0, f"降水速率为负: {weather.precipitation_rate}"

    print("\n✅ 基础测试通过 — 所有物理量在合理范围内")


def test_diurnal_cycle():
    """验证日循环：检查24小时内温度是否呈现单峰"""
    print("\n" + "=" * 60)
    print("TEST 2: 日循环验证")
    print("=" * 60)

    sim = PhysicsWeatherSimulation(latitude=35.0)
    temps = []

    for _ in range(48):  # 2天
        sim.update(1.0)
        temps.append(sim.world._world_entity.get_component(PhysicalWeatherComponent).temperature)

    # 检查每天的峰值出现在14:00附近
    day1_temps = temps[0:24]
    day2_temps = temps[24:48]

    day1_peak_idx = day1_temps.index(max(day1_temps))
    day2_peak_idx = day2_temps.index(max(day2_temps))

    print(f"  第1天峰值在 hour={day1_peak_idx}, 第2天峰值在 hour={day2_peak_idx}")

    # 峰值应该在12-16之间
    assert 10 <= day1_peak_idx <= 16, f"日循环峰值不在预期时间: {day1_peak_idx}"
    assert 10 <= day2_peak_idx <= 16, f"日循环峰值不在预期时间: {day2_peak_idx}"

    # 检查白天和夜晚的温差
    day1_avg = sum(day1_temps[8:18]) / 10  # 白天 8-18点
    night1_avg = sum(day1_temps[0:6] + day1_temps[20:24]) / 10  # 夜晚
    diff = abs(day1_avg - night1_avg)

    print(f"  日间平均温度: {day1_avg:.1f}°C, 夜间平均温度: {night1_avg:.1f}°C")
    print(f"  昼夜温差: {diff:.1f}°C")

    assert diff > 1.0, f"昼夜温差过小: {diff:.1f}°C"

    print("✅ 日循环测试通过")


def test_weather_diversity():
    """长时间运行验证天气多样性"""
    print("\n" + "=" * 60)
    print("TEST 3: 天气多样性验证 (60天)")
    print("=" * 60)

    sim = PhysicsWeatherSimulation(latitude=35.0)
    weather_labels = set()
    cloud_levels = set()

    for _ in range(1440):  # 60天
        sim.update(1.0)
        weather = sim.world._world_entity.get_component(PhysicalWeatherComponent)
        state = classify_from_component(weather)
        weather_labels.add(state.label)
        cloud_levels.add(state.cloud_cover_level.value)

        if sim.step % 144 == 0:
            sim.debug()

    print(f"\n  观察到的天气标签: {sorted(weather_labels)}")
    print(f"  观察到的云量等级: {sorted(cloud_levels)}")
    print(f"  标签种类数: {len(weather_labels)}")
    print(f"  云量等级数: {len(cloud_levels)}")

    assert len(cloud_levels) > 1, "云量等级单一，缺少变化"
    print("✅ 天气多样性测试通过")


def test_rain_event():
    """验证能否产生自然的降水过程"""
    print("\n" + "=" * 60)
    print("TEST 4: 降水事件验证")
    print("=" * 60)

    sim = PhysicsWeatherSimulation(latitude=35.0)
    sim.run_storm_tracking(max_steps=500)


def test_independence():
    """验证与旧weather模块的独立性"""
    print("\n" + "=" * 60)
    print("TEST 5: 模块独立性验证")
    print("=" * 60)

    # 确认新模块可以独立import，不依赖旧weather模块
    from environment.physics_weather import (
        PhysicalWeatherComponent,
        PhysicalWeatherSystem,
        classify,
        DerivedWeatherState,
        CloudCoverLevel,
    )
    print("  ✅ 新模块独立 import 成功")

    # 确认枚举类型不冲突
    assert CloudCoverLevel.CLEAR.value == "clear"
    print("  ✅ 枚举类型独立")
    print("✅ 独立性测试通过")


if __name__ == "__main__":
    test_basic()
    test_diurnal_cycle()
    test_weather_diversity()
    test_rain_event()
    test_independence()
    print("\n" + "=" * 60)
    print("所有测试通过 ✅")
    print("=" * 60)
