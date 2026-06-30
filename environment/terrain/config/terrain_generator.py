# AI Generated
"""
地形生成器
用于程序化生成地形
"""

import random
import math
from typing import List, Tuple
from core.world import World
from space.space_component import SpaceComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.terrain.config.terrain_types import TerrainType
from core.sqrt_cache import cached_sqrt, cached_distance


class TerrainGenerator:
    """
    地形生成器

    使用噪声函数生成真实感的地形
    """

    def __init__(self, world: World):
        self.world = world

    def generate_terrain_grid(
        self,
        width: int,
        height: int,
        layer: int = 0,
        seed: int = 0
    ) -> List[int]:
        """
        生成地形网格

        Args:
            width: 网格宽度
            height: 网格高度
            layer: 空间层
            seed: 随机种子

        Returns:
            实体ID列表
        """
        if seed is not None:
            random.seed(seed)

        entities = []

        # 生成基础高度场
        height_field = self._generate_height_field(width, height)

        # 创建地形实体
        for x in range(width):
            for y in range(height):
                entity = self.world.create_entity()

                # 创建空间组件
                space = SpaceComponent(x=x, y=y, layer=layer)
                self.world.add_component(entity, space)

                # 创建地形组件
                terrain = self._create_terrain_from_height(
                    height_field[y][x],
                    x, y, width, height
                )
                self.world.add_component(entity, terrain)

                entities.append(entity.id)

        return entities

    def _generate_height_field(self, width: int, height: int) -> List[List[float]]:
        """
        生成高度场（简化版噪声）

        使用多层噪声叠加生成自然地形
        """
        field = [[0.0 for _ in range(width)] for _ in range(height)]

        # 叠加多层噪声
        for octave in range(4):
            frequency = 2 ** octave
            amplitude = 1.0 / (2 ** octave)

            for y in range(height):
                for x in range(width):
                    # 简化的噪声函数
                    noise = self._noise(
                        x * frequency / width,
                        y * frequency / height
                    )
                    field[y][x] += noise * amplitude

        # 归一化到0-2000米范围
        max_height = max(max(row) for row in field)
        min_height = min(min(row) for row in field)

        for y in range(height):
            for x in range(width):
                field[y][x] = (
                    (field[y][x] - min_height) / (max_height - min_height)
                ) * 2000

        return field

    def _noise(self, x: float, y: float) -> float:
        """
        简化的噪声函数

        使用正弦波叠加模拟噪声
        """
        return (
            math.sin(x * math.pi * 2) * math.cos(y * math.pi * 2) +
            math.sin(x * math.pi * 4 + 1) * math.cos(y * math.pi * 4 + 1) * 0.5 +
            math.sin(x * math.pi * 8 + 2) * math.cos(y * math.pi * 8 + 2) * 0.25
        ) / 1.75

    def _create_terrain_from_height(
        self,
        elevation: float,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> TerrainComponent:
        """
        根据高度创建地形组件
        """
        # 计算坡度和坡向（简化）
        slope = 0.0
        aspect = 0.0

        if x > 0 and x < width - 1 and y > 0 and y < height - 1:
            # 使用中心差分计算梯度
            dx = (elevation - elevation) / 2  # 简化，实际需要相邻点高度
            dy = (elevation - elevation) / 2

            slope = cached_distance(dx, dy)
            aspect = math.degrees(math.atan2(dy, dx)) % 360

        # 根据高度设置其他属性
        if elevation > 1500:
            # 山地
            vegetation_cover = random.uniform(0.0, 0.3)
            vegetation_height = random.uniform(0, 5)
        elif elevation > 500:
            # 丘陵
            vegetation_cover = random.uniform(0.3, 0.7)
            vegetation_height = random.uniform(2, 10)
        elif elevation < 0:
            # 山谷
            vegetation_cover = random.uniform(0.6, 0.9)
            vegetation_height = random.uniform(5, 15)
        else:
            # 平原
            vegetation_cover = random.uniform(0.1, 0.5)
            vegetation_height = random.uniform(0, 3)

        return TerrainComponent(
            elevation=elevation,
            slope=slope,
            aspect=aspect,
            roughness=random.uniform(0.0, 0.3),
            curvature=random.uniform(-0.1, 0.1),
            vegetation_cover=vegetation_cover,
            vegetation_height=vegetation_height,
            vegetation_type=self._get_vegetation_type(vegetation_cover)
        )

    def _get_vegetation_type(self, cover: float) -> str:
        """
        根据植被覆盖率获取植被类型
        """
        if cover > 0.8:
            return "dense_forest"
        elif cover > 0.6:
            return "forest"
        elif cover > 0.4:
            return "woodland"
        elif cover > 0.2:
            return "grassland"
        else:
            return "sparse"
