#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
农业-环境耦合系统

职责：
    - 施肥增加土壤养分
    - 收割降低植被覆盖
"""

import logging
from typing import Dict, Tuple

from core.system import System
from core.world import World
from space.space_component import SpaceComponent
from environment.soil.components.soil_component import SoilComponent
from human.components.interaction.gathering_component import GatheringComponent

logger = logging.getLogger(__name__)


class AgricultureCouplingSystem(System):
    """农业-环境耦合系统"""

    tick_interval = 20
    FERTILIZER_N_BOOST = 10.0   # 氮肥增量 (mg/kg)
    FERTILIZER_P_BOOST = 5.0    # 磷肥增量 (mg/kg)
    FERTILIZER_K_BOOST = 15.0   # 钾肥增量 (mg/kg)

    def update(self, world: World, dt: float = 1.0) -> None:
        """处理农业活动影响"""
        for entity, (space, gathering) in world.get_components(
            SpaceComponent, GatheringComponent
        ):
            soil = world.get_component(entity, SoilComponent)
            if soil is None:
                continue

            if hasattr(gathering, 'fertilizing') and gathering.fertilizing:
                if hasattr(soil, 'nutrient_n'):
                    soil.nutrient_n += self.FERTILIZER_N_BOOST * dt
                if hasattr(soil, 'nutrient_p'):
                    soil.nutrient_p += self.FERTILIZER_P_BOOST * dt
                if hasattr(soil, 'nutrient_k'):
                    soil.nutrient_k += self.FERTILIZER_K_BOOST * dt

            if hasattr(gathering, 'harvesting') and gathering.harvesting:
                if hasattr(soil, 'vegetation_cover'):
                    soil.vegetation_cover = max(0.0, soil.vegetation_cover - 0.1 * dt)
