#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECS 性能基准测试脚本
量化优化前后的性能指标：步速、内存占用、CPU利用率
"""
import time
import os
import sys
import psutil
import logging
sys.path.insert(0, os.path.abspath('.'))

from core.world import World
from full_simulation import FullSimulationLoop

# 关闭日志
logging.basicConfig(level=logging.WARNING)
process = psutil.Process(os.getpid())

def benchmark(name: str, steps: int = 200, population: int = 100):
    """运行基准测试"""
    print(f"\n{'='*60}")
    print(f"基准测试: {name}")
    print(f"参数: 人口={population}, 步数={steps}")
    print(f"{'='*60}")

    # 初始化世界
    world = World()
    sim = FullSimulationLoop(world)
    sim.init()
    sim.create_initial_resources()
    sim.create_initial_population(population)
    
    # 预热10步
    for i in range(10):
        sim.update(1.0)
    
    # 运行测试
    mem_before = process.memory_info().rss / 1024 / 1024
    start = time.perf_counter()
    
    for i in range(steps):
        sim.update(1.0)
    
    end = time.perf_counter()
    mem_after = process.memory_info().rss / 1024 / 1024
    
    # 计算指标
    duration = end - start
    steps_per_sec = steps / duration
    ms_per_step = duration / steps * 1000
    mem_used = mem_after - mem_before

    print(f"耗时: {duration:.2f}s")
    print(f"速度: {steps_per_sec:.1f} 步/秒")
    print(f"单步耗时: {ms_per_step:.2f} ms/步")
    print(f"内存占用: {mem_after:.1f} MB (增长 {mem_used:.1f} MB)")
    print(f"实体数量: {world.get_entity_count()}")

    return {
        "name": name,
        "steps": steps,
        "population": population,
        "duration": duration,
        "steps_per_sec": steps_per_sec,
        "ms_per_step": ms_per_step,
        "mem_mb": mem_after,
        "mem_growth_mb": mem_used,
    }

def benchmark_soa_access():
    """测试SoA字段数组访问性能（待补充组件路径）"""
    print(f"\n{'='*60}")
    print(f"基准测试: SoA vs AoS 字段访问性能 待实现")
    print(f"{'='*60}")
    return 0, 0

if __name__ == "__main__":
    # 运行基准测试
    results = []
    
    # 基础测试
    results.append(benchmark("100人口", population=100, steps=200))
    results.append(benchmark("500人口", population=500, steps=100))
    results.append(benchmark("1000人口", population=1000, steps=50))
    
    # SoA性能测试
    ao_dur, soa_dur = benchmark_soa_access()

    print(f"\n{'='*60}")
    print(f"基准测试完成")
    print(f"{'='*60}")
