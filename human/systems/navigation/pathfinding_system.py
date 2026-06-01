#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
PathfindingSystem - 路径规划系统

职责：
- 为 MOVE_TO 动作的实体提供 A* 寻路
- 考虑 SpaceMap 边界和障碍物
- 生成路径点序列，供 MovementSystem 逐点执行

注意：当前 SpaceMap 无内置障碍物数据，障碍物通过 SpaceSystem 查询动态实体位置。
"""

import math
import heapq
from typing import List, Tuple, Optional, Set

from core.system import System
from core.world import World

from space.space_component import SpaceComponent
from space.space_system import SpaceSystem
from core.components.action_component import (
    ActionComponent, ActionType, ActionStatus
)


class PathfindingSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    路径规划系统

    在 MovementSystem 之前执行，为需要移动的实体预计算路径。
    若目标被阻挡，寻找最近可达点。
    """

    priority = 28  # 在 CombatAISystem(29) 之前

    def __init__(self, max_steps: int = 100):
        super().__init__()
        self.max_steps = max_steps

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)

        space_system: SpaceSystem = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (space, action) in world.get_components(
            SpaceComponent, ActionComponent
        ):
            if action.current_action != ActionType.MOVE_TO:
                continue

            target = action.target_pos
            if target is None:
                continue

            target_x, target_y = int(target[0]), int(target[1])
            start_x, start_y = int(space.x), int(space.y)

            # 如果已经在目标点，无需寻路
            if (start_x, start_y) == (target_x, target_y):
                continue

            # 执行 A* 寻路
            path = self._astar(
                start=(start_x, start_y),
                goal=(target_x, target_y),
                space_system=space_system,
                exclude_entity_id=entity.id,
            )

            if path and len(path) > 1:
                # 将完整路径存入 action 的扩展属性
                # MovementSystem 会读取 path 并逐点移动
                action._path = path[1:]  # 去掉当前位置
                action._path_index = 0
                # 下一个 immediate target
                next_pos = path[1]
                action.target_pos = (float(next_pos[0]), float(next_pos[1]))
            else:
                # 无可达路径
                action._path = []
                action._path_index = 0

    def _astar(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        space_system: SpaceSystem,
        exclude_entity_id: int,
    ) -> List[Tuple[int, int]]:
        """
        A* 寻路算法

        Args:
            start: 起点 (x, y)
            goal: 终点 (x, y)
            space_system: 空间系统，用于查询障碍物
            exclude_entity_id: 排除的实体ID（寻路实体自身）

        Returns:
            路径点列表（包含起点和终点），不可达返回空列表
        """
        # 获取世界边界
        world_width = getattr(space_system, 'map_width', 100)
        world_height = getattr(space_system, 'map_height', 100)

        # 查询当前所有实体位置作为动态障碍物
        occupied: Set[Tuple[int, int]] = set()
        for eid, comp in space_system.components.items():
            if eid != exclude_entity_id:
                occupied.add((int(comp.x), int(comp.y)))

        # 如果目标点被占据，尝试找最近可达点
        goal = self._find_nearest_free(goal, occupied, world_width, world_height)
        if goal == start:
            return [start]

        # A*
        open_set = [(0, 0, start)]  # (f_score, tie_breaker, node)
        g_score = {start: 0}
        came_from = {}
        counter = 1  # tie breaker

        while open_set:
            _, _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct_path(came_from, current, start)

            if g_score[current] >= self.max_steps:
                continue

            for neighbor in self._neighbors(current, world_width, world_height):
                if neighbor in occupied:
                    continue

                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, counter, neighbor))
                    counter += 1

        # 不可达：返回直线路径（退化到原行为）
        return []

    @staticmethod
    def _heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """欧几里得距离启发函数"""
        return math.hypot(a[0] - b[0], a[1] - b[1])

    @staticmethod
    def _neighbors(
        pos: Tuple[int, int], width: int, height: int
    ) -> List[Tuple[int, int]]:
        """获取四邻域（上下左右）"""
        x, y = pos
        result = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
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
        """从 came_from 重建路径"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    @staticmethod
    def _find_nearest_free(
        goal: Tuple[int, int],
        occupied: Set[Tuple[int, int]],
        width: int,
        height: int,
        max_radius: int = 5,
    ) -> Tuple[int, int]:
        """
        如果目标点被占据，寻找最近的可达点
        """
        if goal not in occupied:
            return goal

        gx, gy = goal
        for r in range(1, max_radius + 1):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) + abs(dy) != r:
                        continue
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if (nx, ny) not in occupied:
                            return (nx, ny)
        return goal  #  fallback
