#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
土壤质量系统

管理 SoilQualityComponent 的动态演化：
- 自然肥力衰减与恢复
- 污染影响（预留）
"""

from core.system import System
from core.world import World

from environment.soil.components.soil_quality_component import SoilQualityComponent


class SoilQualitySystem(System):
    """土壤质量维护系统"""

    tick_interval = 20
    priority = 15

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)
        for entity, (quality) in world.get_components(SoilQualityComponent):
            # 土壤质量向自然均值 0.6 缓慢回归
            if quality.quality > 0.6:
                quality.quality = max(0.6, quality.quality - 0.001)
            elif quality.quality < 0.6:
                quality.quality = min(0.6, quality.quality + 0.001)
