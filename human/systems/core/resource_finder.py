#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:resource_finder.py
@说明:资源查找器

职责：
    - 查找可收获的植物
    - 在记忆中查找资源
    - 查找最近的资源
'''

import math


class ResourceFinder:
    """资源查找器"""

    def find_harvestable_plant(self, entity, world):
        """查找附近可收获的植物"""
        from space.space_component import SpaceComponent
        from biology.organisms.plant.components.plant_component import PlantComponent

        space = world.get_component(entity, SpaceComponent)
        if space is None:
            return None

        # 查询附近的植物
        from space.space_system import SpaceSystem
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return None

        nearby = space_system.query_radius(space.x, space.y, 10)
        for target_id in nearby:
            if target_id == entity.id:
                continue
            target = world.query_entity(target_id)
            if target is None:
                continue
            plant = world.get_component(target, PlantComponent)
            if plant is not None and getattr(plant, 'is_harvestable', False):
                return target

        return None

    def find_resource_in_memory(self, entity, world, resource_type: str):
        """在记忆中查找资源"""
        from human.components.cognitive.memory_component import MemoryComponent

        memory = world.get_component(entity, MemoryComponent)
        if memory is None:
            return None

        # 查找记忆中的资源位置
        if hasattr(memory, 'places'):
            for place_id, place_info in memory.places.items():
                if place_info.get('type') == resource_type:
                    return place_id

        return None

    def find_nearest_resource(self, entity, world, resource_type: str):
        """查找最近的资源"""
        from space.space_component import SpaceComponent
        from space.space_system import SpaceSystem

        space = world.get_component(entity, SpaceComponent)
        if space is None:
            return None

        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return None

        # 查询附近的实体
        nearby = space_system.query_radius(space.x, space.y, 50)
        nearest = None
        nearest_dist = float('inf')

        for target_id in nearby:
            if target_id == entity.id:
                continue
            target = world.query_entity(target_id)
            if target is None:
                continue

            # 检查是否是目标资源类型
            from resource.components.resource_component import ResourceComponent
            resource = world.get_component(target, ResourceComponent)
            if resource is not None and resource.resource_type == resource_type:
                target_space = world.get_component(target, SpaceComponent)
                if target_space is not None:
                    dist = math.hypot(space.x - target_space.x, space.y - target_space.y)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest = target

        return nearest