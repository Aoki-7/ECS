#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:identity_system.py
@说明:身份更新系统
@时间:2026/03/15 22:58:34
@作者:Sherry
@版本:1.0
'''


from core.system import System
from core.world import World

from human.components.basic.identity_component import IdentityComponent


class IdentitySystem(System):
    tick_interval = 10  # 每10帧执行一次

    def update(self, world: World, dt: float):
        for entity, [identity] in world.get_components(IdentityComponent):
            identity: IdentityComponent

            # -------------------------
            # 1. 基础身份属性合法性约束
            # -------------------------
            if not identity.name:
                identity.name = "Unknown"

            # -------------------------
            # 2. 阵营变化
            # -------------------------
            self._update_faction(entity, identity, world)

    # =
    # 阵营演化
    # =
    def _update_faction(self, entity, identity: IdentityComponent, world):
        # 示例：没有阵营 → 自动归为"neutral"
        if not identity.faction:
            identity.faction = "neutral"

        # 这里可以扩展：
        # - 根据行为系统改变阵营
        # - 根据群体系统归属
        # - 根据地理系统归属
