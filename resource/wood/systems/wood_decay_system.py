#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:wood_decay_system.py
@说明:木材腐朽系统
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.0
'''

from core.system import System
from core.world import World

from resource.wood.components.wood_component import WoodComponent


class WoodDecaySystem(System):

    def update(self, world: World, dt: float):
        for entity, [wood] in world.get_components(WoodComponent):
            wood: WoodComponent
            # 更新木材腐朽
            wood.update_decay(dt)