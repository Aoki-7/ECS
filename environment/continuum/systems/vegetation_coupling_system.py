#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植被-环境耦合系统

职责：
    - 植被蒸腾增加局部湿度
    - 植被覆盖影响热扩散阻尼
"""

import logging
from typing import Dict, Optional, Tuple

from core.system import System
from core.world import World
from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent

logger = logging.getLogger(__name__)


class VegetationCouplingSystem(System):
    """植被-环境耦合系统"""

    tick_interval = 20
    TRANSPIRATION_RATE = 0.005  # 蒸腾速率 (湿度/h)

    def update(self, world: World, dt: float = 1.0) -> None:
        """处理植被影响"""
        grid = self._get_environment_grid(world)
        for key, eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            terrain = world.get_component(eid, TerrainComponent)
            if env is None or terrain is None:
                continue

            if terrain.vegetation_cover > 0:
                transpiration = terrain.vegetation_cover * self.TRANSPIRATION_RATE * dt
                env.air_humidity = min(1.0, env.air_humidity + transpiration)

    def _get_environment_grid(self, world: World) -> Dict:
        """获取环境网格"""
        grid = {}
        for entity, (env) in world.get_components(EnvironmentComponent):
            grid[(0, 0)] = entity.id  # 简化处理
        return grid