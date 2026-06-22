#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动物-环境耦合系统

职责：
    - 动物踩踏增加土壤紧实度
    - 动物挖掘影响土壤扰动
"""

import logging
from typing import Dict, Tuple

from core.system import System
from core.world import World
from space.space_component import SpaceComponent
from environment.soil.components.soil_component import SoilComponent
from animal.components.animal_component import AnimalComponent

logger = logging.getLogger(__name__)


class AnimalCouplingSystem(System):
    """动物-环境耦合系统"""

    tick_interval = 20
    TRAMPLING_COMPACTION = 0.01  # 踩踏紧实度增加 (1/h)

    def update(self, world: World, dt: float = 1.0) -> None:
        """处理动物活动影响"""
        animal_counts = self._count_animals_per_grid(world)

        for key, count in animal_counts.items():
            soil = world.get_component(key, SoilComponent)
            if soil is None:
                continue

            compaction = count * self.TRAMPLING_COMPACTION * dt
            if hasattr(soil, 'compaction'):
                soil.compaction = min(1.0, soil.compaction + compaction)
            elif hasattr(soil, 'soil_type'):
                if soil.soil_type == "sand" and compaction > 0.1:
                    soil.soil_type = "loam"

    def _count_animals_per_grid(self, world: World) -> Dict:
        """统计每个网格的动物数量"""
        animal_counts = {}
        for entity, (space, animal) in world.get_components(SpaceComponent, AnimalComponent):
            key = entity.id
            animal_counts[key] = animal_counts.get(key, 0) + 1
        return animal_counts
