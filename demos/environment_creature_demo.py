#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境模块 + 生物 Demo

持续运行一个完整环境管线，并在网格上投放若干带有生理需求的简化生物，
观察环境变化对生物状态的影响。

用法：
    python demos/environment_creature_demo.py --steps 200 --grid 10 --creatures 5
    python demos/environment_creature_demo.py --steps 500 --grid 20 --creatures 10 --quiet
"""

import argparse
import os
import sys
import time

# 确保能从项目根导入
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from core.world import World

from environment.config.environment_builder import EnvironmentBuilder
from environment.environment_factory import EnvironmentFactory
from environment.environment_component import EnvironmentComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.light_field.components.surface_light_component import SurfaceLightComponent
from environment.light_field.components.solar_position_component import SolarPositionComponent

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
# 基础设施
# ════════════════════════════════════════════════════════════


def _build_world(grid_size: int):
    """初始化带完整环境管线和网格的世界。"""
    world = World()

    # 世界实体 + 时间
    we = world.create_entity()
    time_comp = TimeComponent(hour=6.0)  # 从早上开始，便于观察昼夜
    world.add_component(we, time_comp)
    world.set_world_entity(we)
    world.set_time(time_comp)

    # 环境管线
    pipeline = EnvironmentBuilder.build(world)

    # 环境网格
    factory = EnvironmentFactory(world)
    factory.create_environment_grid(grid_size, grid_size)

    # 设置 world.get_environment() 引用，供生物效果系统读取
    world_env = world.get_world_component(EnvironmentComponent)
    world.set_environment(world_env)

    return world, pipeline, time_comp


def _advance_time(time_comp: TimeComponent, dt: float = 1.0) -> None:
    """推进世界时间。"""
    time_comp.total_hours += dt
    time_comp.hour += dt
    if time_comp.hour >= time_comp.day_hours:
        time_comp.hour -= time_comp.day_hours
        time_comp.day_of_year += 1
        if time_comp.day_of_year > time_comp.days_per_year:
            time_comp.day_of_year = 1
            time_comp.year += 1


def _spawn_creature(world: World, x: int, y: int, name: str):
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
    world.add_component(entity, LifeCycleComponent(current_age=5.0, max_age=80.0))
    return entity


def _creature_stats(world: World, creatures):
    """汇总生物状态。"""
    total_hp = 0.0
    total_thirst = 0.0
    total_comfort = 0.0
    alive = 0
    for entity in creatures:
        health = world.get_component(entity, HealthStatusComponent)
        needs = world.get_component(entity, PhysiologyNeedsComponent)
        if health is None or needs is None:
            continue
        total_hp += health.hp
        total_thirst += needs.thirst
        total_comfort += needs.comfort
        if health.hp > 0:
            alive += 1
    n = len(creatures)
    return {
        "alive": alive,
        "avg_hp": total_hp / n if n else 0.0,
        "avg_thirst": total_thirst / n if n else 0.0,
        "avg_comfort": total_comfort / n if n else 0.0,
    }


# ════════════════════════════════════════════════════════════
# 主函数
# ════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="环境模块 + 生物持续运行 Demo"
    )
    parser.add_argument(
        "--steps", type=int, default=200, help="运行步数（默认 200）"
    )
    parser.add_argument(
        "--grid", type=int, default=10, help="环境网格大小 N×N（默认 10）"
    )
    parser.add_argument(
        "--creatures", type=int, default=5, help="投放生物数量（默认 5）"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="仅输出最终汇总"
    )
    parser.add_argument(
        "--report", action="store_true", help="打印环境管线结构"
    )
    args = parser.parse_args()

    world, pipeline, time_comp = _build_world(args.grid)

    if args.report:
        print(pipeline.report())
        print()

    # 环境对生物的影响系统
    effect_systems = [
        ColdEffectSystem(),
        HeatEffectSystem(),
        HumidityEffectSystem(),
        RainEffectSystem(),
    ]

    # 投放生物
    creatures = []
    for i in range(args.creatures):
        x = (i * 2) % args.grid
        y = (i * 3) % args.grid
        creatures.append(_spawn_creature(world, x, y, f"creature_{i}"))

    print(
        f"[Demo] 环境网格 {args.grid}×{args.grid}，"
        f"投放 {args.creatures} 个生物，运行 {args.steps} 步..."
    )
    print("-" * 70)

    start_ts = time.perf_counter()
    max_temp = -1e9
    min_temp = 1e9
    max_rain = 0.0
    day_night_switches = 0
    last_daytime = None

    for step in range(args.steps):
        world.tick_count = step
        _advance_time(time_comp, 1.0)
        pipeline.update(world, 1.0)
        for system in effect_systems:
            system.update(world, 1.0)

        env = world.get_environment()
        weather = world.get_world_component(PhysicalWeatherComponent)
        light = world.get_world_component(SurfaceLightComponent)

        max_temp = max(max_temp, weather.temperature)
        min_temp = min(min_temp, weather.temperature)
        max_rain = max(max_rain, weather.precipitation_rate)

        if last_daytime is not None and env.is_daytime != last_daytime:
            day_night_switches += 1
        last_daytime = env.is_daytime

        if not args.quiet and step % 10 == 0:
            c_stats = _creature_stats(world, creatures)
            print(
                f"[step {step:4d}] "
                f"hour={time_comp.hour:5.1f} "
                f"T={weather.temperature:5.1f}°C "
                f"RH={weather.relative_humidity:4.2f} "
                f"rain={weather.precipitation_rate:6.3f} "
                f"light={env.light_level:5.3f} "
                f"day={env.is_daytime!s:5} "
                f"| creatures alive={c_stats['alive']}/{args.creatures} "
                f"avg_hp={c_stats['avg_hp']:5.1f} "
                f"thirst={c_stats['avg_thirst']:5.1f} "
                f"comfort={c_stats['avg_comfort']:5.1f}"
            )

    elapsed = time.perf_counter() - start_ts

    print("-" * 70)
    print(
        f"[Done] {args.steps} 步完成，耗时 {elapsed:.2f}s "
        f"({args.steps / elapsed:.1f} 步/s)"
    )
    print(
        f"       时间: hour={time_comp.hour:.1f}, "
        f"day={time_comp.day_of_year}, year={time_comp.year}"
    )
    print(
        f"       环境: T=[{min_temp:.1f}, {max_temp:.1f}]°C, "
        f"rain_peak={max_rain:.3f} mm/h, 昼夜切换 {day_night_switches} 次"
    )
    final_stats = _creature_stats(world, creatures)
    print(
        f"       生物: 存活 {final_stats['alive']}/{args.creatures}, "
        f"avg_hp={final_stats['avg_hp']:.1f}, "
        f"avg_thirst={final_stats['avg_thirst']:.1f}, "
        f"avg_comfort={final_stats['avg_comfort']:.1f}"
    )

    # 如果全部存活且数值有限，视为稳定运行
    assert all(
        world.get_component(e, HealthStatusComponent).hp >= 0
        for e in creatures
    ), "存在生物 hp 为负，运行不稳定"
    print("       状态检查通过：环境持续运行，生物数值有界。")


if __name__ == "__main__":
    main()