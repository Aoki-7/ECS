#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纯生态系统模拟 — CLI 入口

运行方式：
    python ecosystem_main.py [steps] [plant_count] [herbivore_count] [carnivore_count]

示例：
    python ecosystem_main.py 200 100 20 5
"""

import sys
import logging

# 修复 Windows 终端中文乱码
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

from core.world import World
from application.ecosystem_loop import EcosystemLoop


def main():
    """主函数"""
    # 解析命令行参数
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    plant_count = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    herbivore_count = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    carnivore_count = int(sys.argv[4]) if len(sys.argv) > 4 else 5

    print("=" * 60)
    print("  纯生态系统模拟")
    print("=" * 60)
    print(f"  模拟步数: {steps}")
    print(f"  初始植物: {plant_count}")
    print(f"  初始食草动物: {herbivore_count}")
    print(f"  初始食肉动物: {carnivore_count}")
    print("=" * 60)
    print()

    # 创建世界和模拟循环
    world = World()
    loop = EcosystemLoop(world)

    # 创建初始种群
    loop.create_initial_population(
        plant_count=plant_count,
        herbivore_count=herbivore_count,
        carnivore_count=carnivore_count,
    )

    # 运行模拟
    loop.run_simulation(steps=steps, delta_hours=1.0, report_interval=10)

    print()
    print("模拟完成")


if __name__ == "__main__":
    main()
