#!/usr/bin/env python
"""快速测试主函数能否运行5步"""
import time
from core.world import World
from application.simulation_loop import SimulationLoop

world = World()
sim = SimulationLoop(world)
sim.init()
sim.create_initial_resources(food_count=10, water_count=10)
sim.create_initial_plants(plant_count=5)
sim.create_initial_population(human_count=3)

print('=== 模拟开始 ===')
for i in range(5):
    sim.update(delta_hours=1.0)
    print('步', i+1, ': 完成')
    time.sleep(0.1)
print('=== 模拟结束 ===')
print('统计:', sim.get_stats())