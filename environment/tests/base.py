#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基础设施 —— 结果收集器、辅助函数、通用 World 构建器
"""

import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.world import World

# ─────────────────────────────────────────────
# 测试结果收集器
# ─────────────────────────────────────────────


class TestResult:
    """测试结果收集器（线程级单例，由 runner 统一重置）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.reset()
        return cls._instance

    def reset(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def ok(self, msg):
        self.passed += 1
        print(f"  [OK] {msg}")

    def fail(self, msg, detail=""):
        self.failed += 1
        line = f"  [FAIL] {msg}"
        if detail:
            line += f" — {detail}"
        self.errors.append(line)
        print(line)

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'=' * 55}")
        print(f"  测试总结: {total} 项 | "
              f"[OK] {self.passed} 通过 | "
              f"[FAIL] {self.failed} 失败")
        if self.failed > 0:
            print(f"\n  失败明细:")
            for e in self.errors:
                print(f"    {e}")
        print(f"{'=' * 55}")
        return self.failed == 0


# 全局引用（各测试模块统一导入）
T = TestResult()

# ─────────────────────────────────────────────
# World 构建辅助函数
# ─────────────────────────────────────────────


def build_test_world() -> World:
    """创建一个干净的测试用 World"""
    return World()


def setup_weather_world(world: World) -> World:
    """为天气测试准备好世界级组件"""
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.season.season_component import SeasonComponent
    from environment.climate.climate_component import ClimateComponent
    world._world_entity.add_component(PhysicalWeatherComponent())
    world._world_entity.add_component(SeasonComponent())
    world._world_entity.add_component(ClimateComponent())
    return world


def setup_light_world(world: World) -> World:
    """为光照测试准备好世界级组件"""
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
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    world._world_entity.add_component(SolarPositionComponent())
    world._world_entity.add_component(SolarRadiationComponent())
    world._world_entity.add_component(LightScatterComponent())
    world._world_entity.add_component(SurfaceLightComponent())
    world._world_entity.add_component(PhysicalWeatherComponent())
    return world


def setup_soil_world(world: World) -> World:
    """为土壤测试创建基础实体"""
    from environment.physics_weather.components.physical_weather_component import (
        PhysicalWeatherComponent,
    )
    from environment.soil.components.soil_moisture_component import SoilMoistureComponent
    from environment.soil.components.soil_temperature_component import (
        SoilTemperatureComponent,
    )
    world._world_entity.add_component(PhysicalWeatherComponent())
    world._world_entity.add_component(SoilMoistureComponent())
    world._world_entity.add_component(SoilTemperatureComponent())
    return world
