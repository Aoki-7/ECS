#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境模块稳定性测试 —— 长时间运行 + 生物投放

测试目标：
1. 环境管线在 100 步连续运行中不崩溃、数值保持有界。
2. 时间/昼夜/季节正常推进。
3. 投放带生理需求的生物后，环境效果系统（冷/热/湿/雨）能正常读取环境并影响生物。
"""

import math
import sys
import os

# 让脚本独立可运行（pytest 时项目根已在路径中）
if "pytest" not in sys.modules:
    sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..", "..")))

from tests.environment.base import build_test_world, T
from environment.config.environment_builder import EnvironmentBuilder
from environment.environment_factory import EnvironmentFactory
from environment.environment_component import EnvironmentComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.light_field.components.surface_light_component import SurfaceLightComponent
from time_module.time_component import TimeComponent

from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.health_status_component import HealthStatusComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from space.space_component import SpaceComponent
from human.components.basic.identity_component import IdentityComponent

from human.systems.environment.cold_effect_system import ColdEffectSystem
from human.systems.environment.heat_effect_system import HeatEffectSystem
from human.systems.environment.humidity_effect_system import HumidityEffectSystem
from human.systems.environment.rain_effect_system import RainEffectSystem


# ════════════════════════════════════════════════════════════
# 公共辅助函数
# ════════════════════════════════════════════════════════════


def _advance_time(time_comp: TimeComponent, dt: float = 1.0) -> None:
    """手动推进世界时间（环境管线本身不更新 TimeComponent）。"""
    time_comp.total_hours += dt
    time_comp.hour += dt
    if time_comp.hour >= time_comp.day_hours:
        time_comp.hour -= time_comp.day_hours
        time_comp.day_of_year += 1
        time_comp.day_changed = True
        if time_comp.day_of_year > time_comp.days_per_year:
            time_comp.day_of_year = 1
            time_comp.year += 1
            time_comp.year_changed = True
        else:
            time_comp.year_changed = False
    else:
        time_comp.day_changed = False
        time_comp.year_changed = False


def _assert_finite(value: float, name: str) -> None:
    assert value is not None, f"{name} 为 None"
    assert isinstance(value, (int, float)), f"{name} 不是数值: {value!r}"
    assert math.isfinite(value), f"{name} 出现非有限值: {value}"


def _build_environment_world(grid_size: int = 5):
    """构建带完整环境管线和网格的世界。"""
    world = build_test_world()

    # 修复：build_test_world 只把 TimeComponent 挂在世界实体，但未设置 world._time
    time_comp = world.get_world_component(TimeComponent)
    if time_comp is not None:
        world.set_time(time_comp)

    pipeline = EnvironmentBuilder.build(world)
    factory = EnvironmentFactory(world)
    factory.create_environment_grid(grid_size, grid_size)

    # 让 creature effect systems 可以通过 world.get_environment() 拿到环境
    world_env = world.get_world_component(EnvironmentComponent)
    assert world_env is not None, "EnvironmentBuilder 未添加世界级 EnvironmentComponent"
    world.set_environment(world_env)
    return world, pipeline


def _spawn_creature(world, x: int, y: int, name: str) -> int:
    """在指定位置投放一个简化生物。"""
    entity = world.create_entity()
    world.add_component(entity, SpaceComponent(x=x, y=y, layer=0))
    world.add_component(entity, IdentityComponent(name=name))
    world.add_component(
        entity,
        PhysiologyNeedsComponent(
            hunger=20.0,
            thirst=20.0,
            fatigue=20.0,
            energy=80.0,
            comfort=50.0,
        ),
    )
    world.add_component(entity, HealthStatusComponent(hp=100.0, max_hp=100.0))
    world.add_component(entity, LifeCycleComponent(current_age=1.0, max_age=80.0))
    return entity.id


# ════════════════════════════════════════════════════════════
# 测试用例
# ════════════════════════════════════════════════════════════


def test_environment_pipeline_stability():
    """环境管线 100 步连续运行：无崩溃、物理量有界。"""
    print("\n[Environment] 环境管线稳定性测试")
    T.reset()

    world, pipeline = _build_environment_world(grid_size=5)
    time_comp = world.get_world_component(TimeComponent)
    initial_hour = time_comp.hour
    initial_day = time_comp.day_of_year

    temps = []
    lights = []
    rains = []
    daytime_values = []

    steps = 100
    for step in range(steps):
        world.tick_count = step
        _advance_time(time_comp, 1.0)
        pipeline.update(world, 1.0)

        weather = world.get_world_component(PhysicalWeatherComponent)
        light = world.get_world_component(SurfaceLightComponent)
        env = world.get_environment()

        assert weather is not None, f"第 {step} 步：PhysicalWeatherComponent 丢失"
        assert light is not None, f"第 {step} 步：SurfaceLightComponent 丢失"
        assert env is not None, f"第 {step} 步：world environment 丢失"

        _assert_finite(weather.temperature, "temperature")
        _assert_finite(weather.pressure, "pressure")
        _assert_finite(weather.relative_humidity, "relative_humidity")
        _assert_finite(weather.cloud_cover, "cloud_cover")
        _assert_finite(weather.precipitation_rate, "precipitation_rate")
        _assert_finite(weather.wind_speed, "wind_speed")
        _assert_finite(light.direct_light, "direct_light")
        _assert_finite(light.diffuse_light, "diffuse_light")
        _assert_finite(env.air_temperature, "env.air_temperature")
        _assert_finite(env.light_level, "env.light_level")

        # 物理量保持在合理区间（极端值也仍在可接受范围）
        assert -80 <= weather.temperature <= 80, (
            f"第 {step} 步气温越界: {weather.temperature:.2f}°C"
        )
        assert 800 <= weather.pressure <= 1100, (
            f"第 {step} 步气压越界: {weather.pressure:.2f} hPa"
        )
        assert 0 <= weather.relative_humidity <= 1, (
            f"第 {step} 步相对湿度越界: {weather.relative_humidity}"
        )
        assert 0 <= weather.cloud_cover <= 1, (
            f"第 {step} 步云量越界: {weather.cloud_cover}"
        )
        assert weather.precipitation_rate >= 0, (
            f"第 {step} 步降水速率不能为负: {weather.precipitation_rate}"
        )
        assert 0 <= env.light_level <= 2.0, (
            f"第 {step} 步光照水平异常: {env.light_level}"
        )

        temps.append(weather.temperature)
        lights.append(light.direct_light + light.diffuse_light)
        rains.append(weather.precipitation_rate)
        daytime_values.append(env.is_daytime)

    # 时间必须推进（至少小时数变化）
    assert time_comp.hour != initial_hour or time_comp.day_of_year != initial_day, (
        "时间未推进"
    )
    # 昼夜至少切换过一次
    assert any(daytime_values) and not all(daytime_values), "昼夜未发生切换"

    T.ok(
        f"环境管线 {steps} 步稳定运行，温度范围 "
        f"[{min(temps):.1f}, {max(temps):.1f}]°C，"
        f"降水峰值 {max(rains):.2f} mm/h"
    )
    T.summary()


def test_creature_effects_in_environment():
    """向环境中投放生物，检查环境效果系统正常运行。"""
    print("\n[Environment] 生物环境交互测试")
    T.reset()

    world, pipeline = _build_environment_world(grid_size=5)
    effect_systems = [
        ColdEffectSystem(),
        HeatEffectSystem(),
        HumidityEffectSystem(),
        RainEffectSystem(),
    ]

    creatures = []
    for i in range(3):
        eid = _spawn_creature(world, x=i, y=i, name=f"creature_{i}")
        creatures.append(eid)

    # 记录初始状态
    initial_hp = {}
    initial_thirst = {}
    initial_comfort = {}
    for eid in creatures:
        health = world.get_component(eid, HealthStatusComponent)
        needs = world.get_component(eid, PhysiologyNeedsComponent)
        initial_hp[eid] = health.hp
        initial_thirst[eid] = needs.thirst
        initial_comfort[eid] = needs.comfort

    steps = 50
    for step in range(steps):
        world.tick_count = step
        _advance_time(world.get_world_component(TimeComponent), 1.0)
        pipeline.update(world, 1.0)
        for system in effect_systems:
            system.update(world, 1.0)

        # 每一步都检查生物状态合法
        for eid in creatures:
            health = world.get_component(eid, HealthStatusComponent)
            needs = world.get_component(eid, PhysiologyNeedsComponent)
            assert health is not None, f"生物 {eid} HealthStatusComponent 丢失"
            assert needs is not None, f"生物 {eid} PhysiologyNeedsComponent 丢失"
            _assert_finite(health.hp, f"creature {eid} hp")
            _assert_finite(needs.thirst, f"creature {eid} thirst")
            _assert_finite(needs.comfort, f"creature {eid} comfort")
            assert 0 <= health.hp <= health.max_hp, (
                f"生物 {eid} hp 越界: {health.hp}"
            )
            assert 0 <= needs.thirst <= needs.max_thirst, (
                f"生物 {eid} thirst 越界: {needs.thirst}"
            )
            assert 0 <= needs.comfort <= needs.max_comfort, (
                f"生物 {eid} comfort 越界: {needs.comfort}"
            )

    # 额外做一次极端环境测试，确认环境效果系统确实能影响生物状态
    env = world.get_environment()
    env.air_temperature = 40.0  # 高温
    env.air_humidity = 0.2      # 低湿
    world.tick_count += 1
    for system in effect_systems:
        system.update(world, 1.0)

    affected = False
    for eid in creatures:
        needs = world.get_component(eid, PhysiologyNeedsComponent)
        if needs.thirst > initial_thirst[eid] or needs.comfort < initial_comfort[eid]:
            affected = True
            break
    assert affected, "极端高温/低湿环境下生物状态未变化，环境效果系统可能未生效"

    T.ok(f"{len(creatures)} 个生物在环境 {steps} 步中运行正常，极端环境可影响生理状态")
    T.summary()


def test_environment_cell_consistency():
    """环境单元格的同步值与世界级组件保持一致。"""
    print("\n[Environment] 环境单元格一致性测试")
    T.reset()

    world, pipeline = _build_environment_world(grid_size=4)
    _advance_time(world.get_world_component(TimeComponent), 1.0)
    world.tick_count = 1
    pipeline.update(world, 1.0)
    _advance_time(world.get_world_component(TimeComponent), 1.0)
    world.tick_count = 2
    pipeline.update(world, 1.0)

    env_world = world.get_environment()
    world_entity = world.get_world_entity()
    cells = [
        (entity, comps)
        for entity, comps in world.get_components(EnvironmentComponent)
        if entity.id != world_entity.id
    ]
    assert len(cells) == 16, f"预期 16 个环境单元格，实际 {len(cells)}"

    for entity, [env_cell] in cells:
        _assert_finite(env_cell.air_temperature, "cell air_temperature")
        _assert_finite(env_cell.light_level, "cell light_level")
        _assert_finite(env_cell.soil_moisture, "cell soil_moisture")
        # 单元格应从世界级环境同步，温差不会过大（允许局部随机）
        assert abs(env_cell.air_temperature - env_world.air_temperature) <= 30, (
            f"单元格气温与世界级环境偏差过大: "
            f"cell={env_cell.air_temperature}, world={env_world.air_temperature}"
        )

    T.ok(f"{len(cells)} 个环境单元格数值一致且有界")
    T.summary()


if __name__ == "__main__":
    test_environment_pipeline_stability()
    test_creature_effects_in_environment()
    test_environment_cell_consistency()