#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
碰撞检测系统

提供实体间碰撞检测、碰撞响应、障碍物管理。
可被 animal/human/civilization 等模块使用。

v3.0.1 新增
"""

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple

from space.collision_detector import CollisionDetector
from space.collision_resolver import CollisionResolver
from space.collision_querier import CollisionQuerier

from core.component import Component
from core.system import System
from core.world import World


@dataclass(slots=True)
class ColliderComponent(Component):
    """
    碰撞体组件

    定义实体的碰撞形状和属性。
    """
    radius: float = 0.5  # 碰撞半径
    is_solid: bool = True  # 是否为实心（可阻挡其他实体）
    layer: int = 0  # 碰撞层（0=地面实体, 1=建筑, 2=空中）
    mask: int = 0xFFFFFFFF  # 碰撞掩码（与哪些层碰撞）


@dataclass(slots=True)
class ObstacleComponent(Component):
    """
    障碍物组件

    标记不可通行的区域（建筑、岩石、水域等）。
    """
    obstacle_type: str = "wall"  # wall, water, rock, building
    blocks_movement: bool = True
    blocks_vision: bool = True


class CollisionSystem(System):
    """
    碰撞检测系统

    职责：
        - 检测实体间碰撞
        - 检测实体与障碍物碰撞
        - 提供碰撞查询接口
        - 可选：自动分离重叠实体
    """

    tick_interval = 1  # 每帧检查

    def __init__(self, auto_resolve: bool = True):
        super().__init__()
        self.auto_resolve = auto_resolve  # 是否自动分离重叠实体
        self._detector = CollisionDetector()
        self._resolver = CollisionResolver()
        self._querier = CollisionQuerier()

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行碰撞检测和响应"""
        # 获取所有带碰撞体的实体
        colliders = self._collect_colliders(world)
        if len(colliders) < 2:
            return

        # 检测碰撞对
        collisions = self._detector.detect_collisions(world, colliders)

        # 处理碰撞
        for entity_a, entity_b in collisions:
            self._handle_collision(world, entity_a, entity_b)

    def _collect_colliders(self, world: World) -> List[Tuple[int, float, float, float, int, int]]:
        """
        收集所有碰撞体信息

        Returns:
            [(entity_id, x, y, radius, layer, mask), ...]
        """
        from space.space_component import SpaceComponent

        result = []
        for entity, (space, collider) in world.get_components(
            SpaceComponent, ColliderComponent
        ):
            result.append((
                entity.id,
                float(space.x),
                float(space.y),
                collider.radius,
                collider.layer,
                collider.mask,
            ))
        return result

    def _handle_collision(self, world: World, entity_a: int, entity_b: int) -> None:
        """处理单个碰撞"""
        from space.space_component import SpaceComponent

        entity_a_obj = world.query_entity(entity_a)
        entity_b_obj = world.query_entity(entity_b)
        space_a = world.get_component(entity_a_obj, SpaceComponent) if entity_a_obj else None
        space_b = world.get_component(entity_b_obj, SpaceComponent) if entity_b_obj else None

        if space_a is None or space_b is None:
            return

        if self.auto_resolve:
            self._resolver.resolve_overlap(world, entity_a, space_a, entity_b, space_b)

        # 触发碰撞事件
        try:
            world.event_bus.publish("collision", {
                "entity_a": entity_a,
                "entity_b": entity_b,
                "x": (space_a.x + space_b.x) / 2,
                "y": (space_a.y + space_b.y) / 2,
            })
        except Exception:
            pass

    # -------------------------------------------------
    # 公共查询接口（委托给 CollisionQuerier）
    # -------------------------------------------------

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
        """检查指定位置是否有碰撞"""
        return self._querier.check_collision_at(world, x, y, radius, layer, mask, exclude_entity)

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
        """获取与指定位置碰撞的所有实体 ID"""
        return self._querier.get_collisions_at(world, x, y, radius, layer, mask, exclude_entity)

    def is_walkable(
        self,
        world: World,
        x: int,
        y: int,
        mover_entity: Optional[int] = None,
        mover_radius: float = 0.5,
    ) -> bool:
        """检查坐标是否可通行"""
        return self._querier.is_walkable(world, x, y, mover_entity, mover_radius)
