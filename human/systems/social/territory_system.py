#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:territory_system.py
@说明:领地系统（从 TribeSystem 拆分）
@时间:2026/05/30
@版本:1.0

职责：更新部落领地中心为所有成员的平均位置
'''

from core.system import System
from core.world import World

from human.components.social.tribe_component import TribeComponent
from space.space_component import SpaceComponent


class TerritorySystem(System):
    """领地系统 — 维护部落的地理中心"""

    priority = 39

    # 领地中心平滑系数（旧位置权重）
    TERRITORY_SMOOTHING = 0.9

    def update(self, world: World, dt: float):
        for entity, (tribe,) in world.get_components(TribeComponent):
            self._update_territory(world, tribe)

    def _update_territory(self, world: World, tribe: TribeComponent):
        """更新领地中心为所有成员的平均位置"""
        if not tribe.member_ids:
            return

        total_x, total_y = 0, 0
        count = 0
        for member_id in tribe.member_ids:
            entity = world.query_entity(member_id)
            if entity:
                space = world.get_component(entity, SpaceComponent)
                if space:
                    total_x += space.x
                    total_y += space.y
                    count += 1

        if count > 0:
            new_x = total_x / count
            new_y = total_y / count
            old_x, old_y = tribe.home_territory
            tribe.home_territory = (
                old_x * self.TERRITORY_SMOOTHING + new_x * (1.0 - self.TERRITORY_SMOOTHING),
                old_y * self.TERRITORY_SMOOTHING + new_y * (1.0 - self.TERRITORY_SMOOTHING),
            )
