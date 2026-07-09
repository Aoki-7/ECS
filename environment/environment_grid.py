#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境网格 (EnvironmentGrid)

负责按世界配置创建 per-cell 空间环境单元。
每个单元包含 SpaceComponent + EnvironmentComponent + SoilComponent + TerrainComponent，
为 EnvironmentalContinuumSystem 提供扩散/平流/重力水流所需的空间结构。
"""

import logging
from typing import Optional

from core.world import World
from core.components.world_config_component import WorldConfigComponent

from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent
from environment.environment_factory import EnvironmentFactory

logger = logging.getLogger(__name__)


class EnvironmentGrid:
    """
    空间环境网格

    用法:
        grid = EnvironmentGrid(world)
        grid.init_cells()  # 根据 WorldConfigComponent 创建 100x100 单元

    幂等：若已存在带 SpaceComponent 的环境单元，则跳过重复创建。
    """

    def __init__(self, world: World):
        self.world = world
        self._factory = EnvironmentFactory(world)

    def init_cells(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        layer: int = 0,
    ) -> None:
        """
        初始化环境网格。

        Args:
            width: 网格宽度；默认读取 WorldConfigComponent.map_width
            height: 网格高度；默认读取 WorldConfigComponent.map_height
            layer: 空间层；默认 0
        """
        if width is None or height is None:
            cfg = self.world.get_world_component(WorldConfigComponent)
            if cfg is None:
                width = height = 100
            else:
                width = cfg.map_width
                height = cfg.map_height

        # 幂等：只要已存在任意带空间位置的环境单元，就视为已初始化
        for _ in self.world.get_components(SpaceComponent, EnvironmentComponent):
            logger.debug(
                "EnvironmentGrid: existing environment cells detected, skipping init"
            )
            return

        logger.info(f"EnvironmentGrid: creating {width}x{height} environment cells")
        created = self._factory.create_environment_grid(width, height, layer)
        logger.info(f"EnvironmentGrid: created {len(created)} cells")
