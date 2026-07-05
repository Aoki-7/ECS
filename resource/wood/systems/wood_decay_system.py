#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@文件:wood_decay_system.py
@说明:木材腐朽系统
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.1
'''

from core.system import System
from core.world import World

from resource.wood.components.wood_component import WoodComponent


class WoodDecaySystem(System):
    tick_interval = 20  # 每20帧执行一次

    @staticmethod
    def update_wood_decay(wood: WoodComponent, dt: float) -> None:
        """更新木材腐朽"""
        if not wood.is_perishable:
            return

        wood.quality -= wood.decay_rate * dt * (1 + wood.infestation)
        if wood.quality < 0.0:
            wood.quality = 0.0

    def update(self, world: World, dt: float):
        for entity, [wood] in world.get_components(WoodComponent):
            wood: WoodComponent
            self.update_wood_decay(wood, dt)
