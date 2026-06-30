#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
政治系统

管理 PoliticalComponent 的动态演化：
- 影响力自然衰减
- 忠诚度波动
- 外交关系向中立回归
"""

from core.system import System
from core.world import World

from civilization.components.political_component import PoliticalComponent


class PoliticalSystem(System):
    """政治动态系统"""

    tick_interval = 10
    priority = 60

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)
        for entity, (political) in world.get_components(PoliticalComponent):
            # 影响力自然衰减
            if political.influence > 0.0:
                political.influence = max(0.0, political.influence - 0.002)

            # 忠诚度向 0.5 回归
            if political.loyalty > 0.5:
                political.loyalty = max(0.5, political.loyalty - 0.002)
            elif political.loyalty < 0.5:
                political.loyalty = min(0.5, political.loyalty + 0.002)

            # 外交关系向 0 回归
            relations = {}
            for target_id, value in political.diplomatic_relations.items():
                if value > 0:
                    relations[target_id] = max(0.0, value - 0.001)
                elif value < 0:
                    relations[target_id] = min(0.0, value + 0.001)
            political.diplomatic_relations = relations
