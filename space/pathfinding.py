#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用路径规划服务

提供 A* 寻路、流场寻路、直线路径检查等通用路径规划功能。
独立于具体模块，可被 animal/human/civilization 等任意模块使用。

v3.0.1 新增
"""

import math
from typing import Callable, Dict, List, Optional, Set, Tuple


class PathNode:
    """A* 节点"""
    __slots__ = ["x", "y", "g", "h", "f", "parent"]

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.g = 0.0  # 从起点到当前节点的代价
        self.h = 0.0  # 启发式估计到终点的代价
        self.f = 0.0  # 总代价 f = g + h
        self.parent: Optional[PathNode] = None

    def __eq__(self, other) -> bool:
        if isinstance(other, PathNode):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"PathNode({self.x}, {self.y})"


class PathfindingService:
    """
    通用路径规划服务

    职责：
        - A* 寻路（支持障碍物检测）
        - 直线路径检查（视线检测）
        - 路径平滑
        - 最近可达点查找
    """

    # 8 方向邻居偏移
    NEIGHBORS_8 = [
        (-1, -1), (0, -1), (1, -1),
        (-1,  0),          (1,  0),
        (-1,  1), (0,  1), (1,  1),
    ]

    # 4 方向邻居偏移
    NEIGHBORS_4 = [
        (0, -1), (-1, 0), (1, 0), (0, 1),
    ]

    def __init__(self, world_bounds: Optional[Tuple[int, int, int, int]] = None):
        """
        Args:
            world_bounds: (min_x, min_y, max_x, max_y) 世界边界，None 表示无界
        """
        self.world_bounds = world_bounds

    # -------------------------------------------------
    # A* 寻路
    # -------------------------------------------------

    def find_path(
        self,
        start_x: int,
        start_y: int,
        goal_x: int,
        goal_y: int,
        is_walkable: Callable[[int, int], bool],
        allow_diagonal: bool = True,
        max_steps: int = 1000,
    ) -> Optional[List[Tuple[int, int]]]:
        """
        A* 寻路

        Args:
            start_x, start_y: 起点坐标
            goal_x, goal_y: 终点坐标
            is_walkable: (x, y) -> bool，判断坐标是否可通行
            allow_diagonal: 是否允许对角移动
            max_steps: 最大搜索步数，防止无限搜索

        Returns:
            路径点列表（包含起点和终点），不可达返回 None
        """
        # 起点/终点相同
        if start_x == goal_x and start_y == goal_y:
            return [(start_x, start_y)]

        # 终点不可达
        if not is_walkable(goal_x, goal_y):
            return None

        start_node = PathNode(start_x, start_y)
        goal_node = PathNode(goal_x, goal_y)

        open_set: List[PathNode] = [start_node]
        closed_set: Set[Tuple[int, int]] = set()
        open_dict: Dict[Tuple[int, int], PathNode] = {(start_x, start_y): start_node}

        neighbors = self.NEIGHBORS_8 if allow_diagonal else self.NEIGHBORS_4

        steps = 0
        while open_set and steps < max_steps:
            steps += 1

            # 取 f 值最小的节点
            current = min(open_set, key=lambda n: n.f)
            open_set.remove(current)
            del open_dict[(current.x, current.y)]
            closed_set.add((current.x, current.y))

            # 到达目标
            if current == goal_node:
                return self._reconstruct_path(current)

            # 扩展邻居
            for dx, dy in neighbors:
                nx, ny = current.x + dx, current.y + dy

                # 边界检查
                if not self._in_bounds(nx, ny):
                    continue

                # 不可通行
                if not is_walkable(nx, ny):
                    continue

                # 已在关闭集
                if (nx, ny) in closed_set:
                    continue

                # 对角移动时检查拐角
                if allow_diagonal and dx != 0 and dy != 0:
                    if not is_walkable(current.x + dx, current.y) or \
                       not is_walkable(current.x, current.y + dy):
                        continue

                move_cost = math.hypot(dx, dy)
                g = current.g + move_cost

                if (nx, ny) in open_dict:
                    neighbor = open_dict[(nx, ny)]
                    if g < neighbor.g:
                        neighbor.g = g
                        neighbor.f = g + neighbor.h
                        neighbor.parent = current
                else:
                    neighbor = PathNode(nx, ny)
                    neighbor.g = g
                    neighbor.h = self._heuristic(nx, ny, goal_x, goal_y)
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.parent = current
                    open_set.append(neighbor)
                    open_dict[(nx, ny)] = neighbor

        return None  # 不可达或超过步数限制

    def _heuristic(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """启发式函数：欧几里得距离"""
        return math.hypot(x2 - x1, y2 - y1)

    def _reconstruct_path(self, node: PathNode) -> List[Tuple[int, int]]:
        """从终点回溯构建路径"""
        path: List[Tuple[int, int]] = []
        current: Optional[PathNode] = node
        while current:
            path.append((current.x, current.y))
            current = current.parent
        return list(reversed(path))

    def _in_bounds(self, x: int, y: int) -> bool:
        """检查坐标是否在世界边界内"""
        if self.world_bounds is None:
            return True
        min_x, min_y, max_x, max_y = self.world_bounds
        return min_x <= x <= max_x and min_y <= y <= max_y

    # -------------------------------------------------
    # 直线路径检查
    # -------------------------------------------------

    def line_of_sight(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        is_walkable: Callable[[int, int], bool],
    ) -> bool:
        """
        检查两点之间是否有直线视线（无遮挡）

        使用 Bresenham 直线算法。

        Returns:
            True 如果直线上所有点都可通行
        """
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0
        while True:
            if not is_walkable(x, y):
                return False
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return True

    # -------------------------------------------------
    # 路径平滑
    # -------------------------------------------------

    def smooth_path(
        self,
        path: List[Tuple[int, int]],
        is_walkable: Callable[[int, int], bool],
    ) -> List[Tuple[int, int]]:
        """
        路径平滑：移除不必要的中间点

        算法：从起点开始，尽可能跳到最远可见点
        """
        if len(path) <= 2:
            return path

        smoothed: List[Tuple[int, int]] = [path[0]]
        i = 0
        while i < len(path) - 1:
            # 从当前点向后找最远可见点
            j = len(path) - 1
            while j > i:
                if self.line_of_sight(path[i][0], path[i][1],
                                       path[j][0], path[j][1], is_walkable):
                    break
                j -= 1
            smoothed.append(path[j])
            i = j

        return smoothed

    # -------------------------------------------------
    # 最近可达点
    # -------------------------------------------------

    def find_nearest_reachable(
        self,
        start_x: int,
        start_y: int,
        goal_x: int,
        goal_y: int,
        is_walkable: Callable[[int, int], bool],
        max_radius: int = 10,
    ) -> Optional[Tuple[int, int]]:
        """
        查找目标点附近最近的可达点

        当目标点本身不可达时，搜索周围区域找最近的可替代点。
        """
        if is_walkable(goal_x, goal_y):
            return (goal_x, goal_y)

        best: Optional[Tuple[int, int]] = None
        best_dist = float('inf')

        for r in range(1, max_radius + 1):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) != r and abs(dy) != r:
                        continue  # 只检查外圈
                    nx, ny = goal_x + dx, goal_y + dy
                    if not self._in_bounds(nx, ny):
                        continue
                    if is_walkable(nx, ny):
                        dist = math.hypot(nx - goal_x, ny - goal_y)
                        if dist < best_dist:
                            best_dist = dist
                            best = (nx, ny)
            if best:
                break

        return best

    # -------------------------------------------------
    # 流场寻路（大规模单位移动优化）
    # -------------------------------------------------

    def generate_flow_field(
        self,
        goal_x: int,
        goal_y: int,
        is_walkable: Callable[[int, int], bool],
        width: int,
        height: int,
    ) -> Dict[Tuple[int, int], Tuple[int, int]]:
        """
        生成流场（Flow Field）

        适用于大规模单位向同一目标移动的场景（如迁徙、军队移动）。
        预计算每个格子的最优移动方向，运行时 O(1) 查询。

        Returns:
            (x, y) -> (dx, dy) 方向映射
        """
        # Dijkstra 从目标点向外扩展
        from collections import deque

        queue: deque = deque()
        queue.append((goal_x, goal_y))
        distances: Dict[Tuple[int, int], float] = {(goal_x, goal_y): 0.0}
        flow: Dict[Tuple[int, int], Tuple[int, int]] = {}

        while queue:
            cx, cy = queue.popleft()
            cd = distances[(cx, cy)]

            for dx, dy in self.NEIGHBORS_4:
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                if not is_walkable(nx, ny):
                    continue

                nd = cd + 1.0
                if (nx, ny) not in distances or nd < distances[(nx, ny)]:
                    distances[(nx, ny)] = nd
                    queue.append((nx, ny))
                    # 记录流向：从邻居指向当前（即邻居的最佳移动方向）
                    flow[(nx, ny)] = (cx - nx, cy - ny)

        return flow
