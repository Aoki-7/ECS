#!/usr/bin/env python3
"""
ECS 世界模拟引擎 — 统一模拟入口脚本

职责：
    - 作为 CLI 入口，解析参数并启动 SimulationLoop
    - 初始化基础世界状态（人类、植物、食物、水源）
    - 运行标准模拟管线（时间→环境→人类→生物→规则→文明）

核心模拟逻辑已迁移至 application/simulation_loop.py，本模块仅做最轻量的编排。

运行方式：
    python main.py
"""

import sys
import logging

# 修复 Windows 终端中文乱码
sys.stdout.reconfigure(encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

from core.world import World
from application.simulation_loop import SimulationLoop


def main():
    """主函数"""
    logger.info("=== ECS 世界模拟 ===")

    world = World()
    simulation = SimulationLoop(world)
    simulation.init()  # 初始化系统 + 世界配置 + 环境网格
    simulation.create_initial_resources(food_count=80, water_count=80)
    simulation.create_initial_plants(plant_count=30)
    simulation.create_initial_population(human_count=10)
    simulation.run_simulation(steps=1000, delta_hours=1.0, verbose=True)


if __name__ == "__main__":
    main()
