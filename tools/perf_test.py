import time
import os
import sys
import logging
sys.path.insert(0, os.path.abspath('.'))

# 关闭INFO日志，只显示错误
logging.basicConfig(level=logging.WARNING)

from core.world import World
from full_simulation import FullSimulationLoop

# 初始化时间不算，只算模拟步数时间
world = World()
sim = FullSimulationLoop(world)
sim.init()
sim.create_initial_resources()
sim.create_initial_population(10)

start = time.perf_counter()
for i in range(200):
    sim.update(1.0)
end = time.perf_counter()
print(f'200步模拟耗时: {end-start:.2f}s, 速度: {200/(end-start):.1f}步/s')
