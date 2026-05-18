

"""
space_factory.py
空间实体工厂

负责：
- 批量创建Grid空间实体
- 自动挂载SpaceComponent
- 注册到SpaceSystem
"""

from typing import List

from core.world import World

from core.entity import Entity
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem


class SpaceFactory:
    """
    空间实体工厂
    """

    def __init__(self, world: World):

        self.world = world

        # 可选：获取SpaceSystem（用于索引或空间查询）
        self.space_system: SpaceSystem = world.get_system(SpaceSystem)

    # ====
    # 单个空间
    # ====

    def create_cell(
        self,
        x: int,
        y: int,
        layer: int = 0
    ) -> int:
        """
        创建单个空间实体
        """

        # 由world创建entity
        entity = self.world.create_entity()

        space = SpaceComponent(
            x=x,
            y=y,
            layer=layer
        )

        # 挂载component
        self.world.add_component(entity, space)

        # 如果SpaceSystem有索引逻辑，可以同步注册
        if self.space_system:
            self.space_system.add_entity(entity.id, space)

        return entity.id

    # ====
    # 批量生成矩形Grid
    # ====

    def create_grid(
        self,
        width: int,
        height: int,
        layer: int = 0
    ) -> List[int]:
        """
        生成一个矩形Grid空间
        """

        entities = []

        for x in range(width):
            for y in range(height):

                entity_id = self.create_cell(x, y, layer)

                entities.append(entity_id)

        return entities

    # ====
    # 生成指定区域
    # ====

    def create_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        layer: int = 0
    ) -> List[int]:

        entities = []

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):

                entity_id = self.create_cell(x, y, layer)

                entities.append(entity_id)

        return entities

    # ====
    # 多层空间
    # ====

    def create_layers(
        self,
        width: int,
        height: int,
        layers: int
    ) -> List[int]:
        """
        创建多层空间
        """

        entities = []

        for layer in range(layers):

            entities += self.create_grid(width, height, layer)

        return entities