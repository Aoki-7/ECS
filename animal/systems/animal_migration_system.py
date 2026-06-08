#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物迁徙系统（P2 路径规划版）

处理动物的季节性迁徙行为：
    1. 迁徙触发：资源匮乏、季节变化、群体决策
    2. 迁徙路径：A* 路径规划 + 记忆引导
    3. 迁徙状态：准备期 → 移动期 → 定居期
    4. 群体迁徙：社交群体同步迁徙

与 AnimalMemorySystem 的关系：
    - 迁徙目标从记忆中选择（历史食物丰富区域）
    - 迁徙路径沿记忆中的安全通道

与 AnimalSocialSystem 的关系：
    - 群体领袖决定迁徙方向
    - 成员跟随领袖移动
"""

import heapq
import math

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from animal.components.animal_memory_component import AnimalMemoryComponent
from animal.components.animal_social_component import AnimalSocialComponent
from animal.components.animal_territory_component import AnimalTerritoryComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

import logging

logger = logging.getLogger(__name__)


class AnimalMigrationSystem(System):
    tick_interval = 30

    def __init__(self):
        super().__init__()
        self._migration_states: dict[int, str] = {}  # entity_id -> state
        self._migration_paths: dict[int, list[tuple[float, float]]] = {}  # entity_id -> path
        self._path_index: dict[int, int] = {}  # entity_id -> current path index

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新迁徙状态"""
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (animal, needs, memory, space) in world.get_components(
            AnimalComponent, AnimalNeedsComponent, AnimalMemoryComponent, SpaceComponent
        ):
            state = self._migration_states.get(entity.id, "settled")

            if state == "settled":
                self._check_migration_trigger(world, entity, animal, needs, memory, space)
            elif state == "preparing":
                self._prepare_migration(world, entity, animal, memory, space)
            elif state == "migrating":
                self._execute_migration(world, entity, animal, memory, space, dt)

    def _check_migration_trigger(
        self, world: World, entity, animal: AnimalComponent,
        needs: AnimalNeedsComponent, memory: AnimalMemoryComponent, space: SpaceComponent
    ) -> None:
        """检查是否触发迁徙"""
        # 触发条件：饥饿+口渴均高于 0.7，且记忆中有更好的位置
        if needs.hunger < 0.7 and needs.thirst < 0.7:
            return

        # 寻找记忆中的最佳食物源
        best_food = memory.recall_by_type("food")
        if best_food is None:
            return

        # 若记忆中的位置明显更好，触发迁徙
        current_value = self._evaluate_location(world, space)
        if best_food.value > current_value * 1.5:
            self._migration_states[entity.id] = "preparing"
            logger.info(f"[Migration] E{entity.id} 准备迁徙到 ({best_food.x:.0f}, {best_food.y:.0f})")

    def _prepare_migration(
        self, world: World, entity, animal: AnimalComponent,
        memory: AnimalMemoryComponent, space: SpaceComponent
    ) -> None:
        """迁徙准备期：规划路径"""
        # 选择迁徙目标
        target = memory.recall_by_type("food")
        if target is None:
            self._migration_states[entity.id] = "settled"
            return

        # 使用 A* 规划路径
        path = self._astar_pathfinding(space.x, space.y, target.x, target.y, memory)
        if path:
            self._migration_paths[entity.id] = path
            self._path_index[entity.id] = 0
            self._migration_states[entity.id] = "migrating"
            logger.debug(f"[Migration] E{entity.id} 路径规划完成，共 {len(path)} 个路径点")
        else:
            # 路径规划失败，直接移动
            self._migration_paths[entity.id] = [(target.x, target.y)]
            self._path_index[entity.id] = 0
            self._migration_states[entity.id] = "migrating"

        # 群体领袖通知成员
        social = world.get_component(entity, AnimalSocialComponent)
        if social and social.group_id != -1 and social.group_role == "leader":
            self._notify_group_members(world, entity, social.group_id, target)

    def _execute_migration(
        self, world: World, entity, animal: AnimalComponent,
        memory: AnimalMemoryComponent, space: SpaceComponent, dt: float
    ) -> None:
        """执行迁徙移动（沿路径点移动）"""
        path = self._migration_paths.get(entity.id, [])
        index = self._path_index.get(entity.id, 0)

        if not path or index >= len(path):
            # 到达终点
            self._migration_states[entity.id] = "settled"
            memory.add_memory(space.x, space.y, "shelter", value=0.8)
            logger.info(f"[Migration] E{entity.id} 到达迁徙目标")
            return

        # 获取当前目标路径点
        target_x, target_y = path[index]
        dx = target_x - space.x
        dy = target_y - space.y
        dist = math.hypot(dx, dy)

        # 移动速度（受饥饿影响：越饿走得越快）
        needs = world.get_component(entity, AnimalNeedsComponent)
        urgency = 1.0 + (needs.hunger if needs else 0.0)
        move_speed = 2.0 * urgency * dt

        if dist < 1.0:
            # 到达当前路径点，前往下一个
            self._path_index[entity.id] = index + 1
        else:
            # 向路径点移动
            space.x += (dx / dist) * min(move_speed, dist)
            space.y += (dy / dist) * min(move_speed, dist)

    def _astar_pathfinding(
        self, start_x: float, start_y: float,
        target_x: float, target_y: float,
        memory: AnimalMemoryComponent
    ) -> list[tuple[float, float]]:
        """
        A* 路径规划（简化版网格实现）

        使用记忆中的安全位置作为可通行区域，
        威胁位置作为障碍物。
        """
        # 简化的 A*：直接直线 + 记忆引导
        path = []

        # 检查记忆中是否有中间路径点
        intermediate = self._find_safe_waypoints(memory, start_x, start_y, target_x, target_y)

        if intermediate:
            path.append((start_x, start_y))
            path.extend(intermediate)
            path.append((target_x, target_y))
        else:
            # 无中间点，直接直线
            path = self._generate_straight_path(start_x, start_y, target_x, target_y)

        return path

    def _find_safe_waypoints(
        self, memory: AnimalMemoryComponent,
        start_x: float, start_y: float,
        target_x: float, target_y: float
    ) -> list[tuple[float, float]]:
        """从记忆中寻找安全的中间路径点"""
        waypoints = []

        # 获取所有食物和庇护所记忆作为路径点候选
        candidates = []
        candidates.extend(memory.get_memories_by_type("food"))
        candidates.extend(memory.get_memories_by_type("shelter"))

        # 筛选在起点和目标之间的点
        for mem in candidates:
            if mem.strength < 0.3:
                continue
            # 检查是否在路径附近
            if self._is_near_path(mem.x, mem.y, start_x, start_y, target_x, target_y):
                waypoints.append((mem.x, mem.y))

        # 按距离起点排序
        waypoints.sort(key=lambda p: math.hypot(p[0] - start_x, p[1] - start_y))

        # 限制路径点数量
        return waypoints[:3]

    def _is_near_path(
        self, px: float, py: float,
        start_x: float, start_y: float,
        target_x: float, target_y: float,
        max_distance: float = 5.0
    ) -> bool:
        """检查点是否在路径附近"""
        # 计算点到线段的距离
        dx = target_x - start_x
        dy = target_y - start_y
        line_len_sq = dx * dx + dy * dy

        if line_len_sq == 0:
            return math.hypot(px - start_x, py - start_y) <= max_distance

        t = max(0, min(1, ((px - start_x) * dx + (py - start_y) * dy) / line_len_sq))
        nearest_x = start_x + t * dx
        nearest_y = start_y + t * dy

        return math.hypot(px - nearest_x, py - nearest_y) <= max_distance

    def _generate_straight_path(
        self, start_x: float, start_y: float,
        target_x: float, target_y: float,
        step_size: float = 3.0
    ) -> list[tuple[float, float]]:
        """生成直线路径点"""
        path = []
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)

        if dist == 0:
            return [(target_x, target_y)]

        steps = max(1, int(dist / step_size))
        for i in range(1, steps + 1):
            t = i / steps
            path.append((start_x + dx * t, start_y + dy * t))

        return path

    def _evaluate_location(self, world: World, space: SpaceComponent) -> float:
        """评估当前位置的资源价值"""
        # 简化版：查询附近植物密度
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return 1.0

        nearby = space_system.query_radius(x=space.x, y=space.y, r=5.0)
        plant_count = 0
        for eid in nearby:
            entity = world.query_entity(eid)
            if entity and world.get_component(entity, PlantComponent):
                plant_count += 1

        return 1.0 + plant_count * 0.5

    def _notify_group_members(
        self, world: World, leader_entity, group_id: int, target
    ) -> None:
        """通知群体成员开始迁徙"""
        for entity, social in world.get_components(AnimalSocialComponent):
            if social.group_id == group_id and entity.id != leader_entity.id:
                self._migration_states[entity.id] = "preparing"
                logger.debug(f"[Migration] E{entity.id} 响应领袖迁徙号召")
