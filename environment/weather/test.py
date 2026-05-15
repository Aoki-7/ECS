#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
天气系统独立测试脚本

只验证：
- 时间推进是否正常
- 天气系统（云量/降水/温度等）是否随时间演化

运行：
    python weather_test.py
"""

import time

from core.world import World

# 时间系统
from time_module.time_system import TimeSystem

# 环境系统
from environment.config.environment_builder import EnvironmentBuilder
from environment.environment_component import EnvironmentComponent

from environment.weather.components.weather_component import WeatherComponent

class WeatherSimulation:
    def __init__(self):
        self.world = World()

        # 挂载全局环境组件（关键）
        self.world.get_world_entity().add_component(EnvironmentComponent())

        # 初始化系统
        self.time_system = TimeSystem()
        self.env_systems = EnvironmentBuilder.build(self.world)

        self.step = 0
        self.start_time = time.time()

    def update(self, delta_hours=1.0):
        """单步更新"""

        # 1. 时间推进
        self.time_system.update(self.world, delta_hours)

        # 2. 天气系统更新
        for system in self.env_systems:
            system.update(self.world, delta_hours)

        self.step += 1

    def debug_weather(self):
        """打印天气状态（核心观察点）"""
        weather = self.world._world_entity.get_component(WeatherComponent)
        weather: WeatherComponent
        time = self.world.get_time()

        print(f"[Step {self.step}]")
        print(f"  时间: Day {time.day_of_year} Hour {time.hour:.1f}")
        print(weather.to_dict())
        print("-" * 40)

    def run(self, steps=200, delta_hours=1.0, debug_interval=5):
        print("=== 天气系统模拟开始 ===")

        for i in range(steps):
            self.update(delta_hours)

            if i % debug_interval == 0:
                self.debug_weather()

        print("=== 模拟结束 ===")


def main():
    sim = WeatherSimulation()
    sim.run(steps=1000, delta_hours=1.0)


if __name__ == "__main__":
    main()