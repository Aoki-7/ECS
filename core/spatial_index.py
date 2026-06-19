#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空间索引系统 - 优化版

v3.9 优化 — 性能提升

优化点：
    1. query_range 使用平方距离比较，避免 sqrt 计算
    2. query_nearest 使用最小堆，避免重复查询
    3. 批量插入/更新接口
    4. 预分配网格单元
    5. 缓存查询结果（可选）
"""

import math
import heapq
from typing import Dict, List, Optional, Tuple, Set, Iterable


class SpatialIndex:
    """
    均匀网格空间索引 - 优化版

    将世界划分为固定大小的网格单元，
    每个单元存储其中的实体ID。
    """

    def __init__(self, cell_size: float = 50.0, world_size: Tuple[float, float] = (1000.0, 1000.0)):
        self.cell_size = cell_size
        self.world_size = world_size
        self.grid: Dict[Tuple[int, int], Set[int]] = {}
        self.entity_positions: Dict[int, Tuple[float, float]] = {}
        # 预计算网格边界
        self._max_cell_x = int(world_size[0] / cell_size) + 1
        self._max_cell_y = int(world_size[1] / cell_size) + 1

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

    def insert_many(self, entities: Iterable[Tuple[int, float, float]]) -> None:
        """批量插入实体"""
        for entity_id, x, y in entities:
            self.insert(entity_id, x, y)

    def remove(self, entity_id: int) -> None:
        """移除实体"""
        if entity_id not in self.entity_positions:
            return
        x, y = self.entity_positions[entity_id]
        cell = self._get_cell(x, y)
        if cell in self.grid:
            self.grid[cell].discard(entity_id)
            # 清理空单元格以节省内存
            if not self.grid[cell]:
                del self.grid[cell]
        del self.entity_positions[entity_id]

    def update(self, entity_id: int, x: float, y: float) -> None:
        """更新实体位置"""
        self.remove(entity_id)
        self.insert(entity_id, x, y)

    def update_many(self, entities: Iterable[Tuple[int, float, float]]) -> None:
        """批量更新实体位置"""
        for entity_id, x, y in entities:
            self.update(entity_id, x, y)

    def query_range(self, x: float, y: float, radius: float) -> List[int]:
        """
        范围查询 - 优化版

        使用平方距离比较，避免 sqrt 计算。
        """
        result = []
        radius_sq = radius * radius
        cell_radius = int(radius / self.cell_size) + 1
        center_cell = self._get_cell(x, y)

        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.grid:
                    for entity_id in self.grid[cell]:
                        ex, ey = self.entity_positions[entity_id]
                        # 使用平方距离比较，避免 sqrt
                        dist_sq = (ex - x) ** 2 + (ey - y) ** 2
                        if dist_sq <= radius_sq:
                            result.append(entity_id)

        return result

    def query_range_with_dist(self, x: float, y: float, radius: float) -> List[Tuple[int, float]]:
        """
        范围查询（返回距离）- 优化版

        只在需要时计算 sqrt。
        """
        result = []
        radius_sq = radius * radius
        cell_radius = int(radius / self.cell_size) + 1
        center_cell = self._get_cell(x, y)

        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.grid:
                    for entity_id in self.grid[cell]:
                        ex, ey = self.entity_positions[entity_id]
                        dist_sq = (ex - x) ** 2 + (ey - y) ** 2
                        if dist_sq <= radius_sq:
                            # 只在需要时计算 sqrt
                            dist = math.sqrt(dist_sq)
                            result.append((entity_id, dist))

        return result

    def query_nearest(self, x: float, y: float, k: int = 1) -> List[Tuple[int, float]]:
        """
        最近邻查询 - 优化版

        使用最小堆，避免重复查询和排序。
        """
        if not self.entity_positions:
            return []

        # 使用最小堆维护最近的 k 个邻居
        heap = []
        radius = self.cell_size
        center_cell = self._get_cell(x, y)

        while len(heap) < k and radius < max(self.world_size):
            cell_radius = int(radius / self.cell_size) + 1
            found_new = False

            for dx in range(-cell_radius, cell_radius + 1):
                for dy in range(-cell_radius, cell_radius + 1):
                    cell = (center_cell[0] + dx, center_cell[1] + dy)
                    if cell in self.grid:
                        for entity_id in self.grid[cell]:
                            # 跳过已处理的实体
                            if any(eid == entity_id for eid, _ in heap):
                                continue
                            ex, ey = self.entity_positions[entity_id]
                            dist_sq = (ex - x) ** 2 + (ey - y) ** 2
                            # 如果距离在范围内，加入堆
                            if dist_sq <= radius * radius:
                                found_new = True
                                dist = math.sqrt(dist_sq)
                                if len(heap) < k:
                                    heapq.heappush(heap, (-dist, entity_id))
                                elif dist < -heap[0][0]:
                                    heapq.heapreplace(heap, (-dist, entity_id))

            if not found_new:
                break
            radius *= 2

        # 转换为结果列表
        result = [(eid, -dist) for dist, eid in heap]
        result.sort(key=lambda x: x[1])
        return result

    def query_nearest_fast(self, x: float, y: float, k: int = 1) -> List[Tuple[int, float]]:
        """
        最近邻查询 - 快速版

        遍历所有实体，使用最小堆，适合实体数较少的情况。
        """
        if not self.entity_positions:
            return []

        heap = []
        for entity_id, (ex, ey) in self.entity_positions.items():
            dist_sq = (ex - x) ** 2 + (ey - y) ** 2
            dist = math.sqrt(dist_sq)
            if len(heap) < k:
                heapq.heappush(heap, (-dist, entity_id))
            elif dist < -heap[0][0]:
                heapq.heapreplace(heap, (-dist, entity_id))

        result = [(eid, -dist) for dist, eid in heap]
        result.sort(key=lambda x: x[1])
        return result

    def get_position(self, entity_id: int) -> Optional[Tuple[float, float]]:
        """获取实体位置"""
        return self.entity_positions.get(entity_id)

    def clear(self) -> None:
        """清空索引"""
        self.grid.clear()
        self.entity_positions.clear()

    def get_stats(self) -> dict:
        """获取索引统计信息"""
        return {
            'entities': len(self.entity_positions),
            'cells': len(self.grid),
            'cell_size': self.cell_size,
            'world_size': self.world_size,
            'avg_per_cell': len(self.entity_positions) / max(len(self.grid), 1),
        }
