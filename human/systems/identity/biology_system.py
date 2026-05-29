#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:biology_system.py
@说明:
@时间:2026/03/19 16:17:21
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World

from human.components.biology.biology_component import SpeciesComponent


class BiologySystem(System):

    def __init__(self):
        self.year_per_time = 0.01

    def update(self, world: World, dt: float):
        for entity, [bio] in world.get_components(SpeciesComponent):
            bio: SpeciesComponent
            
            # -------------------------
            # 1. 年龄增长
            # -------------------------
            bio.age += self.year_per_time * dt

            # -------------------------
            # 2. 年龄合法性约束
            # -------------------------
            if bio.age < 0:
                bio.age = 0

            # -------------------------
            # 3. 年龄阶段标签
            # -------------------------
            self._update_age_stage(entity, bio)

    def _update_age_stage(self, entity, bio: SpeciesComponent):
        # 清理旧标签
        if hasattr(entity, "remove_tag"):
            entity.remove_tag("child")
            entity.remove_tag("adult")
            entity.remove_tag("elder")

        # 添加新标签
        if hasattr(entity, "add_tag"):
            if bio.age < 14:
                entity.add_tag("child")
            elif bio.age < 60:
                entity.add_tag("adult")
            else:
                entity.add_tag("elder")
