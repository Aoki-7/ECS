

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:space_system.py
@说明:空间核心系统
@时间:2026/03/09 13:01:36
@作者:Sherry
@版本:1.0
'''

from typing import Dict, Set, Tuple, List

from space.space_component import SpaceComponent
from space.spatial_index import SpatialIndex

class SpaceSystem():
    """
    SpaceSystem

    ECS空间系统，用于管理实体在Grid空间中的位置与查询。

    负责：
    - 注册实体
    - 删除实体
    - 移动实体
    - 空间查询

    特点
    - 稀疏Grid
    - O(1)移动
    - 高效邻域查询
    - 支持Layer
    - 世界尺寸无限

    """
    def __init__(self):
        self.index = SpatialIndex()

        # entity_id -> SpaceComponent
        self.components: Dict[int, SpaceComponent] = {}

        # 脏实体集合，避免 update 时全量扫描
        self._dirty_entities: Set[int] = set()

    # ====
    # Entity lifecycle
    # ====

    def add_entity(self, entity_id: int, comp: SpaceComponent):
        """添加实体"""
        self.components[entity_id] = comp

        self.index.add(entity_id, comp.x, comp.y, comp.layer)

        comp.dirty = False
        self._dirty_entities.discard(entity_id)

    # -----------------------------------------------------

    def remove_entity(self, entity_id: int):
        """删除实体"""
        if entity_id not in self.components:
            return

        self.index.remove(entity_id)

        del self.components[entity_id]
        self._dirty_entities.discard(entity_id)

    # ====
    # Movement
    # ====

    def move(self, entity_id: int, x: int, y: int, layer: int = 0):
        """空间移动"""
        comp = self.components.get(entity_id)

        if comp is None:
            return

        if layer is None:
            layer = comp.layer

        comp.x = x
        comp.y = y
        comp.layer = layer

        comp.dirty = True
        self._dirty_entities.add(entity_id)

    # -----------------------------------------------------

    def update(self, world=None, dt: float = None):
        """
        同步所有dirty实体
        """
        for entity_id in list(self._dirty_entities):
            comp = self.components.get(entity_id)
            if comp is None:
                continue

            self.index.move(entity_id, comp.x, comp.y, comp.layer)
            comp.dirty = False

        self._dirty_entities.clear()

    # ====
    # Queries
    # ====

    def entities_at(self, x: int, y: int, layer: int = 0) -> Set[int]:
        """查询指定位置上的实体"""
        return self.index.entities_at(x, y, layer)

    # -----------------------------------------------------

    def neighbors(
        self,
        x: int,
        y: int,
        r: int = 1,
        layer: int = 0
    ) -> Set[int]:
        """查询指定位置周围的实体"""
        result: Set[int] = set()

        for i in range(x - r, x + r + 1):
            for j in range(y - r, y + r + 1):

                result |= self.index.entities_at(i, j, layer)

        return result

    # -----------------------------------------------------

    def query_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        layer: int = 0
    ) -> Set[int]:
        """
            查询指定矩形区域内的实体
        """
        result: Set[int] = set()

        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):

                result |= self.index.entities_at(i, j, layer)

        return result

    # -----------------------------------------------------

    def query_radius(
        self,
        x: float,
        y: float,
        r: float,
        layer: int = 0
    ) -> Set[int]:
        """查询指定圆形区域内的实体"""
        result: Set[int] = set()

        r2 = r * r

        for i in range(int(x - r), int(x + r) + 1):
            for j in range(int(y - r), int(y + r) + 1):

                dx = i - x
                dy = j - y

                if dx * dx + dy * dy > r2:
                    continue

                result |= self.index.entities_at(i, j, layer)

        return result
