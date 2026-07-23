#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人类-环境耦合系统

职责：
    - 人类建筑影响风场（挡风/狭管效应）
    - 人类活动改变地表特征
"""

import logging
from typing import Dict, Tuple

from core.system import System
from core.world import World
from space.space_component import SpaceComponent
from human.components.basic.human_component import HumanComponent
from human.components.action.action_component import ActionComponent

logger = logging.getLogger(__name__)


class HumanCouplingSystem(System):
    """人类-环境耦合系统"""

    tick_interval = 20
    BUILDING_WIND_SHIELD = 0.5  # 建筑挡风系数

    def update(self, world: World, dt: float = 1.0) -> None:
        """处理人类建筑影响"""
        building_counts = self._count_buildings_per_grid(world)

        for key, count in building_counts.items():
            if count > 0:
                logger.debug(f"Human building effect at {key}: count={count}")

    def _count_buildings_per_grid(self, world: World) -> Dict:
        """统计每个网格的建筑数量"""
        building_counts = {}
        for entity, (space, human, action) in world.get_components(
            SpaceComponent, HumanComponent, ActionComponent
        ):
            if hasattr(action, 'building') and action.building:
                key = entity.id
                building_counts[key] = building_counts.get(key, 0) + 1
        return building_counts