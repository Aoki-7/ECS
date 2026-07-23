#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
碰撞响应器

职责：
    - 分离重叠的实体
    - 处理静态/动态障碍物
"""

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.world import World
    from space.space_component import SpaceComponent


class CollisionResolver:
    """碰撞响应器"""

    def resolve_overlap(
        self,
        world: "World",
        eid_a: int,
        space_a: "SpaceComponent",
        eid_b: int,
        space_b: "SpaceComponent",
    ) -> None:
        """分离重叠的实体"""
        from space.space_system import SpaceSystem
        from space.collision_system import ColliderComponent, ObstacleComponent

        dx = space_b.x - space_a.x
        dy = space_b.y - space_a.y
        dist = math.hypot(dx, dy)

        if dist < 0.001:
            # 完全重叠，随机推开
            dx, dy = 1.0, 0.0
            dist = 1.0

        # 计算分离向量
        entity_a_obj = world.query_entity(eid_a)
        entity_b_obj = world.query_entity(eid_b)
        collider_a = world.get_component(entity_a_obj, ColliderComponent) if entity_a_obj else None
        collider_b = world.get_component(entity_b_obj, ColliderComponent) if entity_b_obj else None
        r_a = collider_a.radius if collider_a else 0.5
        r_b = collider_b.radius if collider_b else 0.5

        overlap = r_a + r_b - dist
        if overlap <= 0:
            return

        # 各移动一半距离
        nx = dx / dist
        ny = dy / dist
        move_a = overlap * 0.5
        move_b = overlap * 0.5

        # 检查哪个实体可以移动（非静态障碍物）
        obs_a = world.get_component(entity_a_obj, ObstacleComponent) if entity_a_obj else None
        obs_b = world.get_component(entity_b_obj, ObstacleComponent) if entity_b_obj else None

        can_move_a = not (obs_a and obs_a.blocks_movement)
        can_move_b = not (obs_b and obs_b.blocks_movement)

        space_system = world.get_system(SpaceSystem)

        if can_move_a and can_move_b:
            space_a.x = int(round(space_a.x - nx * move_a))
            space_a.y = int(round(space_a.y - ny * move_a))
            space_b.x = int(round(space_b.x + nx * move_b))
            space_b.y = int(round(space_b.y + ny * move_b))
        elif can_move_a:
            space_a.x = int(round(space_a.x - nx * overlap))
            space_a.y = int(round(space_a.y - ny * overlap))
        elif can_move_b:
            space_b.x = int(round(space_b.x + nx * overlap))
            space_b.y = int(round(space_b.y + ny * overlap))

        # 标记 dirty
        space_a.dirty = True
        space_b.dirty = True

        if space_system:
            space_system._dirty_entities.add(eid_a)
            space_system._dirty_entities.add(eid_b)