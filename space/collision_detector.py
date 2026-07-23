#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
碰撞检测器

职责：
    - 检测实体间碰撞对
    - 使用 O(n²) 检测（适合实体数 < 1000）
"""

import math
from typing import List, Tuple, Optional

from core.world import World
from space.space_system import SpaceSystem


class CollisionDetector:
    """碰撞检测器"""

    def detect_collisions(
        self,
        world: World,
        colliders: List[Tuple[int, float, float, float, int, int]]
    ) -> List[Tuple[int, int]]:
        """
        检测所有碰撞对

        优先使用空间索引（如果 SpaceSystem 可用），
        回退到 O(n²) 检测。

        Args:
            world: ECS 世界
            colliders: [(entity_id, x, y, radius, layer, mask), ...]

        Returns:
            [(entity_id_a, entity_id_b), ...] 碰撞对列表
        """
        # 尝试使用空间索引加速
        space_system = world.get_system(SpaceSystem)
        if space_system and len(colliders) > 50:
            return self._detect_with_spatial_index(world, colliders, space_system)

        # 实体数较少时，使用简单 O(n²) 检测
        return self._detect_brute_force(colliders)

    def _detect_with_spatial_index(
        self, world: World,
        colliders: List[Tuple[int, float, float, float, int, int]],
        space_system: SpaceSystem
    ) -> List[Tuple[int, int]]:
        """使用空间索引检测碰撞"""
        collisions = []
        checked = set()

        for eid_a, x_a, y_a, r_a, layer_a, mask_a in colliders:
            # 使用空间索引查询附近实体
            nearby = space_system.query_radius(x_a, y_a, r_a * 2)

            for eid_b in nearby:
                if eid_a == eid_b:
                    continue
                if (eid_a, eid_b) in checked or (eid_b, eid_a) in checked:
                    continue

                # 找到 colliders 中 eid_b 的信息
                b_info = None
                for info in colliders:
                    if info[0] == eid_b:
                        b_info = info
                        break

                if b_info is None:
                    continue

                _, x_b, y_b, r_b, layer_b, mask_b = b_info

                # 层掩码检查
                if not (mask_a & (1 << layer_b)):
                    continue
                if not (mask_b & (1 << layer_a)):
                    continue

                # 距离检查
                dist = math.hypot(x_a - x_b, y_a - y_b)
                if dist < r_a + r_b:
                    collisions.append((eid_a, eid_b))
                    checked.add((eid_a, eid_b))

        return collisions

    def _detect_brute_force(
        self,
        colliders: List[Tuple[int, float, float, float, int, int]]
    ) -> List[Tuple[int, int]]:
        """使用 O(n²) 检测所有碰撞对"""
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