#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
碰撞查询器

职责：
    - 检查指定位置是否有碰撞
    - 获取与指定位置碰撞的所有实体
    - 检查坐标是否可通行
"""

import math
from typing import List, Optional, TYPE_CHECKING

from core.world import World
from space.space_component import SpaceComponent

if TYPE_CHECKING:
    from space.collision_system import ColliderComponent, ObstacleComponent


class CollisionQuerier:
    """碰撞查询器"""

    def check_collision_at(
        self,
        world: World,
        x: float,
        y: float,
        radius: float = 0.5,
        layer: int = 0,
        mask: int = 0xFFFFFFFF,
        exclude_entity: Optional[int] = None,
    ) -> bool:
        """
        检查指定位置是否有碰撞

        Returns:
            True 如果该位置与其他实体碰撞
        """
        from space.collision_system import ColliderComponent

        for entity, (space, collider) in world.get_components(
            SpaceComponent, ColliderComponent
        ):
            if exclude_entity is not None and entity.id == exclude_entity:
                continue

            # 层检查
            if not (mask & (1 << collider.layer)):
                continue
            if not (collider.mask & (1 << layer)):
                continue

            dist = math.hypot(space.x - x, space.y - y)
            if dist < radius + collider.radius:
                return True

        return False

    def get_collisions_at(
        self,
        world: World,
        x: float,
        y: float,
        radius: float = 0.5,
        layer: int = 0,
        mask: int = 0xFFFFFFFF,
        exclude_entity: Optional[int] = None,
    ) -> List[int]:
        """
        获取与指定位置碰撞的所有实体 ID
        """
        from space.collision_system import ColliderComponent

        result = []
        for entity, (space, collider) in world.get_components(
            SpaceComponent, ColliderComponent
        ):
            if exclude_entity is not None and entity.id == exclude_entity:
                continue
            if not (mask & (1 << collider.layer)):
                continue
            if not (collider.mask & (1 << layer)):
                continue

            dist = math.hypot(space.x - x, space.y - y)
            if dist < radius + collider.radius:
                result.append(entity.id)

        return result

    def is_walkable(
        self,
        world: World,
        x: int,
        y: int,
        mover_entity: Optional[int] = None,
        mover_radius: float = 0.5,
    ) -> bool:
        """
        检查坐标是否可通行（无障碍物且无其他实体阻挡）

        这是 PathfindingService 的 is_walkable 回调的标准实现。
        """
        from space.collision_system import ColliderComponent, ObstacleComponent

        # 检查障碍物
        for entity, (space, obs) in world.get_components(
            SpaceComponent, ObstacleComponent
        ):
            if not obs.blocks_movement:
                continue
            if space.x == x and space.y == y:
                return False

        # 检查其他实体碰撞体
        for entity, (space, collider) in world.get_components(
            SpaceComponent, ColliderComponent
        ):
            if mover_entity is not None and entity.id == mover_entity:
                continue
            if not collider.is_solid:
                continue

            dist = math.hypot(space.x - x, space.y - y)
            if dist < mover_radius + collider.radius:
                return False

        return True