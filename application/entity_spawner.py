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
        """创建水源（聚落化分布）"""
        from resource.water.water_factory import WaterFactory
        factory = self._factories.get('water', WaterFactory())
        
        num_clusters = random.randint(5, 8)
        margin = 10
        max_cx = world_config.map_width - 1 - margin
        max_cy = world_config.map_height - 1 - margin
        cluster_centers = [
            (random.randint(margin, max_cx), random.randint(margin, max_cy))
            for _ in range(num_clusters)
        ]
        
        for i in range(count):
            cx, cy = random.choice(cluster_centers)
            x = int(random.gauss(cx, 8))
            y = int(random.gauss(cy, 8))
            x = max(0, min(x, world_config.map_width - 1))
            y = max(0, min(y, world_config.map_height - 1))
            factory.create_water(
                self.world, x=x, y=y,
                amount=random.uniform(100, 300)
            )

    def create_initial_population(self, human_count: int = 10) -> None:
        """创建初始人口"""
        from human.human_factory import HumanFactory
        factory = self._factories.get('human', HumanFactory())
        logger.info(f"[Init] 人口: {human_count} 人类")

        for i in range(human_count):
            name = f"Human_{i+1}"
            x, y = random.randint(20, 79), random.randint(20, 79)
            factory.create_human(self.world, name, x, y)

    def create_initial_plants(self, plant_count: int = 30) -> None:
        """创建初始植物"""
        from plant.plant_factory import PlantFactory
        from plant.components.plant_component import PlantComponent
        from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
        from biology.lifecycle.components.morphology_component import MorphologyComponent

        factory = self._factories.get('plant', PlantFactory())
        species_list = list(factory.SPECIES_PRESETS.keys())
        mature_count = 0

        for i in range(plant_count):
            x, y = random.randint(10, 89), random.randint(10, 89)
            species = random.choice(species_list)
            plant = factory.create_plant(self.world, species=species, x=x, y=y, variation=0.15)

            if random.random() < 0.6:
                self._make_plant_mature(plant, species)
                mature_count += 1

        logger.info(f"[Init] 植物: {plant_count} 株（{mature_count} 株成熟可收获）")

    def _make_plant_mature(self, plant: int, species: str) -> None:
        """将植物设为成熟状态"""
        from plant.components.plant_component import PlantComponent
        from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
        from biology.lifecycle.components.morphology_component import MorphologyComponent

        lifecycle = self.world.get_component(plant, LifeCycleComponent)
        plant_comp = self.world.get_component(plant, PlantComponent)
        morph = self.world.get_component(plant, MorphologyComponent)

        if lifecycle is not None:
            lifecycle.stage = LifeCycleComponent.MATURE
            lifecycle.current_age = sum(lifecycle.stage_durations[:3])

        if plant_comp is not None:
            plant_comp.harvestable_yield = random.uniform(8.0, 20.0)
            plant_comp.max_yield = plant_comp.harvestable_yield * 1.5
            if species == "tree":
                plant_comp.produces_wood = True
                plant_comp.wood_amount = random.uniform(2.0, 8.0)

        if morph is not None:
            if species == "tree":
                morph.weight = random.uniform(150.0, 400.0)
            else:
                morph.weight = plant_comp.harvestable_yield * 2.0 if plant_comp else 20.0

    def create_initial_animals(self, animal_count: int = 20) -> None:
        """创建初始动物"""
        from animal.animal_factory import AnimalFactory
        factory = self._factories.get('animal', AnimalFactory())
        logger.info(f"[Init] 动物: {animal_count} 只")

        for i in range(animal_count):
            x, y = random.randint(10, 89), random.randint(10, 89)
            factory.create_animal(self.world, x=x, y=y, species="rabbit")

    def init_environment_grid(self, grid_size: int = 10) -> None:
        """初始化环境网格（若模块存在）"""
        try:
            from environment.grid.environment_grid import EnvironmentGrid
            grid = EnvironmentGrid(self.world, grid_size=grid_size)
            logger.info(f"[Init] 环境网格: {grid_size}x{grid_size}")
        except ImportError:
            logger.warning("[Init] 环境网格模块未找到，跳过初始化")
        except Exception as e:
            logger.warning(f"[Init] 环境网格初始化失败: {e}")
