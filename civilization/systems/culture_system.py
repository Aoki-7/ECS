#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文化系统

管理 CultureComponent 的动态演化：
- 文化认同度自然波动
- 知识传承与衰减
- 习俗/节日列表维护
"""

from core.system import System
from core.world import World

from civilization.components.culture_component import CultureComponent


class CultureSystem(System):
    """文化演化系统"""

    tick_interval = 10  # 每 10 tick 执行一次
    priority = 60       # 在人类社会系统之后

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)
        for entity, culture in world.get_components(CultureComponent):
            # 文化认同度向均值缓慢回归
            if culture.cultural_identity > 0.5:
                culture.cultural_identity = max(0.5, culture.cultural_identity - 0.005)
            elif culture.cultural_identity < 0.5:
                culture.cultural_identity = min(0.5, culture.cultural_identity + 0.005)

            # 知识自然衰减（遗忘），限制下限
            decayed = {}
            for topic, level in culture.knowledge.items():
                decayed[topic] = max(0.0, level - 0.001)
            culture.knowledge = decayed
