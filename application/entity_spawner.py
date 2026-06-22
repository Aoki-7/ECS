#!/usr/bin/env python3
"""
实体生成器

负责初始资源、人口、植物、动物等实体的创建。
将实体生成逻辑从 SimulationLoop 中剥离。
"""

import random
import logging
from typing import List, Tuple, Optional, Any

from core.world import World
from core.components.world_config_component import WorldConfigComponent

logger = logging.getLogger(__name__)


class EntitySpawner:
    """
    实体生成器

    职责：
        1. 初始资源生成（食物、水源）
        2. 初始人口创建
        3. 初始植物创建
        4. 初始动物创建
        5. 环境网格初始化
    """

    def __init__(self, world: World):
        self.world = world
        self._factories = {}

    def register_factory(self, name: str, factory: Any) -> None:
        """注册工厂"""
        self._factories[name] = factory

    def create_initial_resources(self, food_count: int = 80, water_count: int = 80) -> None:
        """创建初始资源"""
        world_config = self.world.get_world_component(WorldConfigComponent)
        if world_config is None:
            logger.warning("[Init] 世界配置未找到，使用默认值")
            world_config = WorldConfigComponent()
        
        logger.info(f"[Init] 资源: {food_count} 食物, {water_count} 水源")
        
        self._create_food(food_count, world_config)
        self._create_water(water_count, world_config)

    def _create_food(self, count: int, world_config: WorldConfigComponent) -> None:
        """创建食物"""
        from resource.food.food_factory import FoodFactory
        factory = self._factories.get('food', FoodFactory())
        for i in range(count):
            x = random.randint(0, world_config.map_width - 1)
            y = random.randint(0, world_config.map_height - 1)
            factory.create_food(
                self.world, x=x, y=y,
                food_type="berry",
                amount=random.uniform(10, 50)
            )

    def _create_water(self, count: int, world_config: WorldConfigComponent) -> None:
        """创建水源"""
        from resource.water.water_factory import WaterFactory
        factory = self._factories.get('water', WaterFactory())
        for i in range(count):
            x = random.randint(0, world_config.map_width - 1)
            y = random.randint(0, world_config.map_height - 1)
            factory.create_water(
                self.world, x=x, y=y,
                amount=random.uniform(50, 200)
            )

    def create_initial_population(self, human_count: int = 10) -> None:
        """创建初始人口"""
        from human.human_factory import HumanFactory
        factory = self._factories.get('human', HumanFactory())
        
        world_config = self.world.get_world_component(WorldConfigComponent)
        if world_config is None:
            world_config = WorldConfigComponent()
        
        for i in range(human_count):
            x = random.randint(0, world_config.map_width - 1)
            y = random.randint(0, world_config.map_height - 1)
            factory.create_human(self.world, name=f"Human_{i}", x=x, y=y)
        
        logger.info(f"[Init] 人口: {human_count} 人类")

    def create_initial_plants(self, plant_count: int = 30) -> None:
        """创建初始植物"""
        from plant.plant_factory import PlantFactory
        factory = self._factories.get('plant', PlantFactory())
        
        world_config = self.world.get_world_component(WorldConfigComponent)
        if world_config is None:
            world_config = WorldConfigComponent()
        
        mature_count = 0
        for i in range(plant_count):
            x = random.randint(0, world_config.map_width - 1)
            y = random.randint(0, world_config.map_height - 1)
            plant = factory.create_plant(self.world, x=x, y=y)
            if plant and hasattr(plant, 'is_mature') and plant.is_mature:
                mature_count += 1
        
        logger.info(f"[Init] 植物: {plant_count} 株（{mature_count} 株成熟可收获）")

    def create_initial_animals(self, animal_count: int = 20) -> None:
        """创建初始动物"""
        from animal.animal_factory import AnimalFactory
        factory = self._factories.get('animal', AnimalFactory())
        
        world_config = self.world.get_world_component(WorldConfigComponent)
        if world_config is None:
            world_config = WorldConfigComponent()
        
        for i in range(animal_count):
            x = random.randint(0, world_config.map_width - 1)
            y = random.randint(0, world_config.map_height - 1)
            factory.create_animal(self.world, x=x, y=y)
        
        logger.info(f"[Init] 动物: {animal_count} 只")

    def init_environment_grid(self) -> None:
        """初始化环境网格"""
        try:
            from environment.environment_grid import EnvironmentGrid
            grid = EnvironmentGrid(self.world)
            grid.init_cells()
            logger.info("[Init] 环境网格已初始化")
        except ImportError:
            logger.warning("[Init] 环境网格模块未找到，跳过初始化")
