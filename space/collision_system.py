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

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行碰撞检测和响应"""
        # 获取所有带碰撞体的实体
        colliders = self._collect_colliders(world)
        if len(colliders) < 2:
            return

        # 检测碰撞对
        collisions = self._detect_collisions(colliders)

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

    def _detect_collisions(
        self,
        colliders: List[Tuple[int, float, float, float, int, int]]
    ) -> List[Tuple[int, int]]:
        """
        检测所有碰撞对

        使用简单 O(n²) 检测，适合实体数 < 1000。
        大规模场景可改用空间索引加速。
        """
        collisions = []
        n = len(colliders)
        for i in range(n):
            eid_a, x_a, y_a, r_a, layer_a, mask_a = colliders[i]
            for j in range(i + 1, n):
                eid_b, x_b, y_b, r_b, layer_b, mask_b = colliders[j]

                # 层掩码检查
                if not (mask_a & (1 << layer_b)):
                    continue
                if not (mask_b & (1 << layer_a)):
                    continue

                # 距离检查
                dist = math.hypot(x_a - x_b, y_a - y_b)
                if dist < r_a + r_b:
                    collisions.append((eid_a, eid_b))

        return collisions

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
            self._resolve_overlap(world, entity_a, space_a, entity_b, space_b)

        # 触发碰撞事件（如果 EventBus 可用）
        try:
            from core.event_bus import EventBus
            bus = EventBus.get_instance()
            bus.publish("collision", {
                "entity_a": entity_a,
                "entity_b": entity_b,
                "x": (space_a.x + space_b.x) / 2,
                "y": (space_a.y + space_b.y) / 2,
            })
        except Exception:
            pass

    def _resolve_overlap(
        self,
        world: World,
        eid_a: int,
        space_a,
        eid_b: int,
        space_b,
    ) -> None:
        """分离重叠的实体"""
        from space.space_system import SpaceSystem

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
        entity_a_obj = world.query_entity(eid_a)
        entity_b_obj = world.query_entity(eid_b)
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

    # -------------------------------------------------
    # 公共查询接口
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
        """
        检查指定位置是否有碰撞

        Returns:
            True 如果该位置与其他实体碰撞
        """
        from space.space_component import SpaceComponent

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
        from space.space_component import SpaceComponent

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
        from space.space_component import SpaceComponent

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
