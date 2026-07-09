# AI Generated
"""
环境工厂
负责批量创建环境实体
"""

from typing import List
import random
from core.world import World
from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent, SoilType
from environment.terrain.components.terrain_component import TerrainComponent
from environment.terrain.config.terrain_types import TerrainType


class EnvironmentFactory:
    """
    环境实体工厂

    负责创建包含完整环境参数的空间实体
    """

    def __init__(self, world: World):
        self.world = world

    def create_environment_cell(
        self,
        x: int,
        y: int,
        layer: int = 0,
        terrain_type: TerrainType = None,
        soil_type: str = None
    ) -> int:
        """
        创建单个环境单元

        包含：
        - SpaceComponent（空间位置）
        - EnvironmentComponent（环境聚合状态）
        - SoilComponent（土壤参数）
        - TerrainComponent（地形参数）
        """
        # 创建实体
        entity = self.world.create_entity()

        # 1. 空间组件
        space = SpaceComponent(x=x, y=y, layer=layer)
        self.world.add_component(entity, space)

        # 2. 环境组件（添加一些随机变化）
        env = EnvironmentComponent(
            par=300.0 + random.uniform(-50, 50),
            air_temperature=20.0 + random.uniform(-5, 5),
            soil_moisture=0.5 + random.uniform(-0.1, 0.1),
            air_humidity=0.6 + random.uniform(-0.1, 0.1),
            wind_speed=0.5 + random.uniform(-0.2, 0.2),
        )
        self.world.add_component(entity, env)

        # 3. 土壤组件
        if soil_type is None:
            soil_type = random.choice([SoilType.SAND, SoilType.LOAM, SoilType.CLAY])

        soil = SoilComponent(
            soil_type=soil_type,
            moisture=0.5 + random.uniform(-0.1, 0.1),
            temperature=18.0 + random.uniform(-3, 3),
            ph=6.5 + random.uniform(-0.5, 0.5),
            nitrogen=50.0 + random.uniform(-10, 10),
            phosphorus=20.0 + random.uniform(-5, 5),
            potassium=60.0 + random.uniform(-10, 10),
        )
        self.world.add_component(entity, soil)

        # 4. 地形组件
        if terrain_type is None:
            terrain_type = random.choice([
                TerrainType.PLAIN,
                TerrainType.PLAIN,
                TerrainType.PLAIN,  # 平原更常见
                TerrainType.HILL,
                TerrainType.FOREST
            ])

        # 根据地形类型设置参数
        if terrain_type == TerrainType.PLAIN:
            elevation = random.uniform(0, 50)
            slope = random.uniform(0, 5)
            vegetation_cover = random.uniform(0.1, 0.3)
        elif terrain_type == TerrainType.HILL:
            elevation = random.uniform(50, 200)
            slope = random.uniform(5, 20)
            vegetation_cover = random.uniform(0.3, 0.6)
        elif terrain_type == TerrainType.FOREST:
            elevation = random.uniform(0, 100)
            slope = random.uniform(0, 10)
            vegetation_cover = random.uniform(0.7, 0.9)
            vegetation_height = random.uniform(5, 15)
        else:
            elevation = 0.0
            slope = 0.0
            vegetation_cover = 0.0

        terrain = TerrainComponent(
            terrain_type=terrain_type,
            elevation=elevation,
            slope=slope,
            aspect=random.uniform(0, 360),
            vegetation_cover=vegetation_cover,
            vegetation_height=getattr(locals(), 'vegetation_height', 0.0),
        )
        self.world.add_component(entity, terrain)

        return entity.id

    def create_environment_grid(
        self,
        width: int,
        height: int,
        layer: int = 0
    ) -> List[int]:
        """
        创建完整的环境网格

        返回所有环境实体的ID列表
        """
        entities = []

        for x in range(width):
            for y in range(height):
                entity_id = self.create_environment_cell(x, y, layer)
                entities.append(entity_id)

        return entities

    def create_environment_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        layer: int = 0,
        terrain_type: TerrainType = None,
        soil_type: str = None
    ) -> List[int]:
        """
        创建指定区域的环境

        返回所有环境实体的ID列表
        """
        entities = []

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                entity_id = self.create_environment_cell(
                    x, y, layer, terrain_type, soil_type
                )
                entities.append(entity_id)

        return entities
