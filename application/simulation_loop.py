#!/usr/bin/env python3
"""
统一模拟主循环（重构版）

采用组合模式，将职责委托给：
- SystemRegistry: 系统注册中心
- EntitySpawner: 实体生成器
- SimulationDriver: 模拟驱动器
"""

from __future__ import annotations

import time
import random
import sys
import logging

sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

from core.world import World
from core.components.world_config_component import WorldConfigComponent
from core.entity_pool import EntityPool

from application.system_registry import SystemRegistry
from application.entity_spawner import EntitySpawner
from application.simulation_driver import SimulationDriver


class SimulationLoop:
    """
    统一模拟主循环（组合模式）

    职责：
        1. 组合 SystemRegistry、EntitySpawner、SimulationDriver
        2. 提供统一入口
        3. 向后兼容旧 API
    """

    def __init__(self, world: World = None):
        self.world = world or World()
        self.registry = SystemRegistry(self.world)
        self.spawner = EntitySpawner(self.world)
        self.driver = SimulationDriver(self.world)

        # 工厂注册（供 EntitySpawner 使用）
        from resource.food.food_factory import FoodFactory
        from resource.water.water_factory import WaterFactory
        from human.human_factory import HumanFactory
        from plant.plant_factory import PlantFactory
        from animal.animal_factory import AnimalFactory

        self.spawner.register_factory('food', FoodFactory())
        self.spawner.register_factory('water', WaterFactory())
        self.spawner.register_factory('human', HumanFactory())
        self.spawner.register_factory('plant', PlantFactory())
        self.spawner.register_factory('animal', AnimalFactory())

        # 兼容旧属性
        self.food_factory = FoodFactory()
        self.water_factory = WaterFactory()
        self.human_factory = HumanFactory()
        self.plant_factory = PlantFactory()

    def init(self) -> None:
        """初始化：实体池 + 系统 + 环境网格 + 世界配置"""
        self._init_entity_pool()
        self._init_world_config()
        self._init_time()
        self.registry.init_all()
        self.spawner.init_environment_grid()

    def _init_world_config(self) -> None:
        """初始化世界配置（若不存在）"""
        from core.components.world_config_component import WorldConfigComponent
        world_config = self.world.get_world_component(WorldConfigComponent)
        if world_config is None:
            world_config = WorldConfigComponent()
            world_entity = self.world.create_entity()
            self.world.add_component(world_entity, world_config)
            self.world.set_world_entity(world_entity)
            logger.info(f"[Init] 世界配置已创建: {world_config.map_width}x{world_config.map_height}")

    def _init_time(self) -> None:
        """初始化世界时间组件（若不存在）"""
        if self.world.get_time() is not None:
            return

        from time_module.time_component import TimeComponent
        time = TimeComponent()
        world_entity = self.world.get_world_entity()
        if world_entity is None:
            world_entity = self.world.create_entity()
            self.world.set_world_entity(world_entity)
        self.world.add_component(world_entity, time)
        self.world.set_time(time)
        logger.debug("[Init] 世界时间组件已初始化")

    def _init_entity_pool(self) -> None:
        """初始化实体池"""
        try:
            pool = EntityPool.get_instance()
            import os
            if os.environ.get('ECS_DISABLE_ENTITY_POOL') != '1':
                pool.enable()
                logger.info(f"[Init] 实体池已启用")
            else:
                logger.info("[Init] 实体池已禁用")
        except Exception as e:
            logger.warning(f"[Init] 实体池初始化失败: {e}")

    def create_initial_resources(self, food_count: int = 80, water_count: int = 80) -> None:
        """创建初始资源"""
        self.spawner.create_initial_resources(food_count, water_count)

    def create_initial_population(self, human_count: int = 10) -> None:
        """创建初始人口"""
        self.spawner.create_initial_population(human_count)

    def create_initial_plants(self, plant_count: int = 30) -> None:
        """创建初始植物"""
        self.spawner.create_initial_plants(plant_count)

    def create_initial_animals(self, animal_count: int = 20) -> None:
        """创建初始动物"""
        self.spawner.create_initial_animals(animal_count)

    def run(self, max_steps: int = None, delta_hours: float = 1.0) -> None:
        """运行模拟"""
        self.driver.run(max_steps, delta_hours)

    def run_simulation(self, steps: int = 1000, delta_hours: float = 1.0, verbose: bool = True) -> None:
        """兼容旧 API：运行模拟"""
        self.driver.run(steps, delta_hours)

    def update(self, delta_hours: float = 1.0) -> None:
        """单步更新"""
        self.driver.step(delta_hours)

    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.driver.get_stats()

    # 兼容旧属性访问
    @property
    def step_count(self) -> int:
        return self.driver.step_count

    @property
    def save_load_system(self):
        return self.registry.get('save_load')

    @property
    def time_system(self):
        return self.registry.get('time')

    @property
    def event_log_system(self):
        return self.registry.get('event_log')

    @property
    def env_pipeline(self):
        return self.registry.get('env_pipeline')

    @property
    def pathfinding_system(self):
        return self.registry.get('pathfinding')

    @property
    def collision_system(self):
        return self.registry.get('collision')
