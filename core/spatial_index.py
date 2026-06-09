#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空间索引系统

优化大规模实体的空间查询性能。
实现：均匀网格（Uniform Grid）—— 简单高效，适合中等密度场景。

替代 SpaceSystem 的暴力查询，将 O(n) 降为 O(1) ~ O(k)。
"""

import math
from typing import Dict, List, Optional, Set, Tuple


class SpatialIndex:
    """
    均匀网格空间索引

    将世界划分为固定大小的网格单元，
    每个实体只存储在其所在的单元格中。
    """

    def __init__(self, cell_size: float = 10.0, world_bounds: Optional[Tuple[float, float, float, float]] = None):
        """
        Args:
            cell_size: 网格单元大小
            world_bounds: (min_x, min_y, max_x, max_y) 世界边界
        """
        self.cell_size = cell_size
        self.world_bounds = world_bounds
        self._grid: Dict[Tuple[int, int], Set[int]] = {}  # (cx, cy) -> {entity_id}
        self._entity_cells: Dict[int, Tuple[int, int]] = {}  # entity_id -> (cx, cy)

    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """计算坐标对应的网格单元"""
        return (int(math.floor(x / self.cell_size)), int(math.floor(y / self.cell_size)))

    def add_entity(self, entity_id: int, x: float, y: float) -> None:
        """添加实体到索引"""
        cell = self._get_cell(x, y)
        if cell not in self._grid:
            self._grid[cell] = set()
        self._grid[cell].add(entity_id)
        self._entity_cells[entity_id] = cell

    def remove_entity(self, entity_id: int) -> None:
        """从索引移除实体"""
        if entity_id in self._entity_cells:
            cell = self._entity_cells[entity_id]
            if cell in self._grid:
                self._grid[cell].discard(entity_id)
                if not self._grid[cell]:
                    del self._grid[cell]
            del self._entity_cells[entity_id]

    def update_entity(self, entity_id: int, x: float, y: float) -> None:
        """更新实体位置（如果跨越单元格则重新分配）"""
        new_cell = self._get_cell(x, y)
        if entity_id in self._entity_cells:
            old_cell = self._entity_cells[entity_id]
            if old_cell == new_cell:
                return  # 仍在同一单元格
            # 从旧单元格移除
            self._grid[old_cell].discard(entity_id)
            if not self._grid[old_cell]:
                del self._grid[old_cell]
        # 添加到新单元格
        if new_cell not in self._grid:
            self._grid[new_cell] = set()
        self._grid[new_cell].add(entity_id)
        self._entity_cells[entity_id] = new_cell

    def query_radius(self, x: float, y: float, radius: float) -> List[int]:
        """
        查询半径内的实体

        算法：
        1. 计算覆盖查询范围的网格单元
        2. 只检查这些单元格内的实体
        """
        center_cell = self._get_cell(x, y)
        cell_radius = int(math.ceil(radius / self.cell_size))

        result = []
        radius_sq = radius * radius

        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self._grid:
                    for entity_id in self._grid[cell]:
                        # 精确距离检查（需要外部提供位置）
                        result.append(entity_id)

        return result

    def query_rect(self, min_x: float, min_y: float, max_x: float, max_y: float) -> List[int]:
        """查询矩形区域内的实体"""
        min_cell = self._get_cell(min_x, min_y)
        max_cell = self._get_cell(max_x, max_y)

        result = []
        for cx in range(min_cell[0], max_cell[0] + 1):
            for cy in range(min_cell[1], max_cell[1] + 1):
                cell = (cx, cy)
                if cell in self._grid:
                    result.extend(self._grid[cell])

        return result

    def get_stats(self) -> dict:
        """获取索引统计"""
        total_entities = len(self._entity_cells)
        total_cells = len(self._grid)
        avg_per_cell = total_entities / total_cells if total_cells > 0 else 0
        max_per_cell = max(len(entities) for entities in self._grid.values()) if self._grid else 0

        return {
            "total_entities": total_entities,
            "total_cells": total_cells,
            "avg_per_cell": avg_per_cell,
            "max_per_cell": max_per_cell,
            "cell_size": self.cell_size,
        }

    def clear(self) -> None:
        """清空索引"""
        self._grid.clear()
        self._entity_cells.clear()
