#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:perception_system.py
@说明:感知系统
@时间:2026/03/28 17:30:09
@作者:Sherry
@版本:1.1
'''

from core.system import System
from core.world import World

from space.space_system import SpaceSystem
from core.components.vision_component import VisionComponent
from space.space_component import SpaceComponent

class PerceptionSystem(System):
    tick_interval = 1  # 每帧执行一次，确保视野信息及时更新
    """
        感知系统
        依赖 SpaceComponent + VisionComponent
        
        观察自身视野范围内的所有实体，并反馈给视野组件
    """
    def update(self, world: World, dt):
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (space, vision) in world.get_components(SpaceComponent, VisionComponent):
            space: SpaceComponent
            vision: VisionComponent

            x, y = space.x, space.y
            r = vision.radius

            # 从SpaceSystem查询视野范围内的实体
            id_list = space_system.query_radius(x=x, y=y, r=r)

            vision.entity_ids = [eid for eid in id_list if eid != entity.id]
            vision.entities = [world.query_entity(eid) for eid in vision.entity_ids]


# 向后兼容的旧拼写别名
PreceptionSystem = PerceptionSystem
