#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
PathfindingSystem - 路径规划系统 - 优化版

v3.9 优化 — 性能提升

优化点：
    1. 使用曼哈顿距离启发函数，避免 sqrt
    2. 八邻域扩展，更自然的路径
    3. 路径缓存，避免重复计算
    4. 增量更新，只重新计算需要更新的路径
    5. 使用 SpatialIndex 查询障碍物，避免遍历所有实体
    6. BFS 寻找最近可达点，替代嵌套循环
"""

import math
import heapq
from typing import List, Tuple, Optional, Set, Dict, Any
from functools import lru_cache

from core.system import System
from core.world import World

from space.space_component import SpaceComponent
from space.space_system import SpaceSystem
from human.components.action.action_component import (
    ActionComponent, ActionType, ActionStatus
)


class PathfindingSystem(System):
    tick_interval = 1
    priority = 28

    def __init__(self, max_steps: int = 100):
        super().__init__()
        self.max_steps = max_steps
        # 路径缓存：{(start, goal): (path, timestamp)}
        self._path_cache: Dict[Tuple[Tuple[int, int], Tuple[int, int]], Tuple[List[Tuple[int, int]], int]] = {}
        self._cache_ttl = 10  # 缓存有效期（ticks）
        self._tick_count = 0

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)
        self._tick_count += 1

        space_system: SpaceSystem = world.get_system(SpaceSystem)
        if space_system is None:
            return

        # 使用 SpatialIndex 加速障碍物查询
        spatial_index = getattr(space_system, 'spatial_index', None)

        for entity, (space, action) in world.get_components(
            SpaceComponent, ActionComponent
        ):
            if action.current_action != ActionType.MOVE_TO:
                continue

            # 如果目标实体已被删除，清理路径缓存
            if getattr(action, 'target_entity', None) is not None:
                if world.query_entity(action.target_entity) is None:
                    action._path = []
                    action._path_index = 0
                    continue

            target = action.target_pos
            if target is None:
                continue

            target_x, target_y = int(target[0]), int(target[1])
            start_x, start_y = int(space.x), int(space.y)

            # 如果已经在目标点，无需寻路
            if (start_x, start_y) == (target_x, target_y):
                continue

            # 检查缓存
            cache_key = ((start_x, start_y), (target_x, target_y))
            cached = self._path_cache.get(cache_key)
            if cached is not None:
                path, timestamp = cached
                if self._tick_count - timestamp < self._cache_ttl:
                    # 缓存有效，直接使用
                    if path and len(path) > 1:
                        action._path = path[1:]
                        action._path_index = 0
                        next_pos = path[1]
                        action.target_pos = (float(next_pos[0]), float(next_pos[1]))
                    continue
                else:
                    # 缓存过期，删除
                    del self._path_cache[cache_key]

            # 执行 A* 寻路
            path = self._astar(
                start=(start_x, start_y),
                goal=(target_x, target_y),
                space_system=space_system,
                spatial_index=spatial_index,
                exclude_entity_id=entity.id,
            )

            if path and len(path) > 1:
                # 缓存路径
                self._path_cache[cache_key] = (path, self._tick_count)
                action._path = path[1:]
                action._path_index = 0
                next_pos = path[1]
                action.target_pos = (float(next_pos[0]), float(next_pos[1]))
            else:
                action._path = []
                action._path_index = 0

    def _astar(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        space_system: SpaceSystem,
        spatial_index: Optional[Any],
        exclude_entity_id: int,
    ) -> List[Tuple[int, int]]:
        """A* 寻路算法 - 优化版"""
        world_width = getattr(space_system, 'map_width', 100)
        world_height = getattr(space_system, 'map_height', 100)

        # 获取障碍物 - 使用 SpatialIndex 加速
        occupied: Set[Tuple[int, int]] = set()
        if spatial_index is not None:
            # 使用 SpatialIndex 查询目标附近的实体
            nearby = spatial_index.query_range(goal[0], goal[1], max(world_width, world_height))
            for eid in nearby:
                if eid != exclude_entity_id:
                    pos = spatial_index.get_position(eid)
                    if pos:
                        occupied.add((int(pos[0]), int(pos[1])))
        else:
            # 回退到遍历所有实体
            for eid, comp in space_system.components.items():
                if eid != exclude_entity_id:
                    occupied.add((int(comp.x), int(comp.y)))

        # 如果目标点被占据，找最近可达点
        goal = self._find_nearest_free_bfs(goal, occupied, world_width, world_height)
        if goal == start:
            return [start]

        # A* 算法
        open_set = [(0, 0, start)]
        g_score = {start: 0}
        came_from = {}
        counter = 1

        while open_set:
            _, _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct_path(came_from, current, start)

            if g_score[current] >= self.max_steps:
                continue

            for neighbor in self._neighbors_8(current, world_width, world_height):
                if neighbor in occupied:
                    continue

                # 八邻域移动代价：直线 1，对角线 1.414
                dx = abs(neighbor[0] - current[0])
                dy = abs(neighbor[1] - current[1])
                move_cost = 1.414 if dx + dy == 2 else 1.0

                tentative_g = g_score[current] + move_cost

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self._heuristic_manhattan(neighbor, goal)
                    heapq.heappush(open_set, (f_score, counter, neighbor))
                    counter += 1

        return []

    @staticmethod
    def _heuristic_manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """曼哈顿距离启发函数 - 无 sqrt"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def _neighbors_8(
        pos: Tuple[int, int], width: int, height: int
    ) -> List[Tuple[int, int]]:
        """八邻域（上下左右 + 对角线）"""
        x, y = pos
        result = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0),
                       (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                result.append((nx, ny))
        return result

    @staticmethod
    def _reconstruct_path(
        came_from: dict,
        current: Tuple[int, int],
        start: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """重建路径"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    @staticmethod
    def _find_nearest_free_bfs(
        goal: Tuple[int, int],
        occupied: Set[Tuple[int, int]],
        width: int,
        height: int,
        max_radius: int = 5,
    ) -> Tuple[int, int]:
        """
        使用 BFS 寻找最近的可达点 - 替代嵌套循环
        """
        if goal not in occupied:
            return goal

        from collections import deque
        queue = deque([(goal, 0)])
        visited = {goal}

        while queue:
            (x, y), dist = queue.popleft()
            if dist > max_radius:
                break

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) not in occupied:
                        return (nx, ny)
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), dist + 1))

        return goal

    def clear_cache(self) -> None:
        """清理路径缓存"""
        self._path_cache.clear()