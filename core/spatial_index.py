#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空间索引系统

v3.6 新增 — 性能优化

职责：
    - 为 O(n²) 系统提供空间查询加速
    - 支持范围查询、最近邻查询
    - 动态更新实体位置

设计原则：
    - 纯物理位置索引
    - 无业务逻辑
"""

import math
from typing import Dict, List, Optional, Tuple, Set


class SpatialIndex:
    """
    均匀网格空间索引

    将世界划分为固定大小的网格单元，
    每个单元存储其中的实体ID。
    """

    def __init__(self, cell_size: float = 50.0, world_size: Tuple[float, float] = (1000.0, 1000.0)):
        self.cell_size = cell_size
        self.world_size = world_size
        self.grid: Dict[Tuple[int, int], Set[int]] = {}
        self.entity_positions: Dict[int, Tuple[float, float]] = {}

    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """获取坐标对应的网格单元"""
        return (int(x / self.cell_size), int(y / self.cell_size))

    def insert(self, entity_id: int, x: float, y: float) -> None:
        """插入实体"""
        cell = self._get_cell(x, y)
        if cell not in self.grid:
            self.grid[cell] = set()
        self.grid[cell].add(entity_id)
        self.entity_positions[entity_id] = (x, y)

    def remove(self, entity_id: int) -> None:
        """移除实体"""
        if entity_id not in self.entity_positions:
            return
        x, y = self.entity_positions[entity_id]
        cell = self._get_cell(x, y)
        if cell in self.grid:
            self.grid[cell].discard(entity_id)
        del self.entity_positions[entity_id]

    def update(self, entity_id: int, x: float, y: float) -> None:
        """更新实体位置"""
        self.remove(entity_id)
        self.insert(entity_id, x, y)

    def query_range(self, x: float, y: float, radius: float) -> List[int]:
        """范围查询"""
        result = []
        cell_radius = int(radius / self.cell_size) + 1
        center_cell = self._get_cell(x, y)

        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.grid:
                    for entity_id in self.grid[cell]:
                        ex, ey = self.entity_positions[entity_id]
                        dist = math.hypot(ex - x, ey - y)
                        if dist <= radius:
                            result.append(entity_id)

        return result

    def query_nearest(self, x: float, y: float, k: int = 1) -> List[Tuple[int, float]]:
        """最近邻查询"""
        # 扩展搜索半径直到找到k个邻居
        radius = self.cell_size
        result = []

        while len(result) < k and radius < max(self.world_size):
            candidates = self.query_range(x, y, radius)
            for entity_id in candidates:
                ex, ey = self.entity_positions[entity_id]
                dist = math.hypot(ex - x, ey - y)
                result.append((entity_id, dist))

            # 排序并取最近的k个
            result.sort(key=lambda x: x[1])
            result = result[:k]
            radius *= 2

        return result

    def clear(self) -> None:
        """清空索引"""
        self.grid.clear()
        self.entity_positions.clear()
