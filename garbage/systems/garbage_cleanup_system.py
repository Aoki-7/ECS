#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:garbage_cleanup_system.py
@说明:垃圾清理系统
@时间:2026/05/26
@版本:1.0
'''

from core.system import System
from core.world import World

from garbage.components.garbage_component import GarbageComponent


class GarbageCleanupSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    垃圾清理系统
    
    定期清理世界中的垃圾实体，防止僵尸实体无限积累。
    策略：当垃圾实体数超过阈值时，删除最旧的垃圾。
    """

    def __init__(self, max_garbage: int = 50):
        super().__init__()
        self.max_garbage = max_garbage

    def update(self, world: World, dt: float):
        garbage_entities = []
        for entity, [garbage] in world.get_components(GarbageComponent):
            garbage_entities.append(entity)

        excess = len(garbage_entities) - self.max_garbage
        if excess > 0:
            # 简单策略：删除 ID 最小的（通常是最早创建的）
            garbage_entities.sort(key=lambda e: e.id)
            for entity in garbage_entities[:excess]:
                world.remove_entity(entity)
