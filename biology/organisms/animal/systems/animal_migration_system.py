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

import math

from core.system import System
from core.world import World

from biology.organisms.animal.components.animal_component import AnimalComponent
from biology.organisms.animal.components.animal_needs_component import AnimalNeedsComponent
from biology.organisms.animal.components.animal_memory_component import AnimalMemoryComponent
from biology.organisms.animal.components.animal_social_component import AnimalSocialComponent
from biology.organisms.animal.components.animal_territory_component import AnimalTerritoryComponent
from biology.organisms.animal.migration.components.migration_component import MigrationComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem
from space.pathfinding import PathfindingService

import logging

logger = logging.getLogger(__name__)


class AnimalMigrationSystem(System):
    tick_interval = 30

    def __init__(self):
        super().__init__()
        self._migration_states: dict[int, str] = {}  # entity_id -> state
        self._migration_paths: dict[int, list[tuple[float, float]]] = {}  # entity_id -> path
        self._path_index: dict[int, int] = {}  # entity_id -> current path index
        self._pathfinding = PathfindingService(world_bounds=(0, 0, 100, 100))

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新迁徙状态"""
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (animal, needs, memory, space) in world.get_components(
            AnimalComponent, AnimalNeedsComponent, AnimalMemoryComponent, SpaceComponent
        ):
            # 检查是否有迁徙组件
            migration = world.get_component(entity, MigrationComponent)
            if migration is not None and migration.is_migratory:
                # 使用新迁徙系统
                self._update_migration_component(world, entity, migration, animal, space, dt)
                continue

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
        # 使用通用路径规划服务（v3.0.1）
        path = self._pathfinding.find_path(
            int(space.x), int(space.y),
            int(target.x), int(target.y),
            is_walkable=lambda x, y: self._is_walkable_for_animal(world, x, y, memory),
            allow_diagonal=True,
            max_steps=200,
        )
        if path:
            # 平滑路径
            smoothed = self._pathfinding.smooth_path(
                path,
                is_walkable=lambda x, y: self._is_walkable_for_animal(world, x, y, memory),
            )
            self._migration_paths[entity.id] = smoothed
            self._path_index[entity.id] = 0
            self._migration_states[entity.id] = "migrating"
            if logger.isEnabledFor(logging.DEBUG):
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[Migration] E{entity.id} 路径规划完成，共 {len(smoothed)} 个路径点")
        else:
            # 路径规划失败，尝试最近可达点
            nearest = self._pathfinding.find_nearest_reachable(
                int(space.x), int(space.y),
                int(target.x), int(target.y),
                is_walkable=lambda x, y: self._is_walkable_for_animal(world, x, y, memory),
                max_radius=10,
            )
            if nearest:
                self._migration_paths[entity.id] = [nearest]
                self._path_index[entity.id] = 0
                self._migration_states[entity.id] = "migrating"
            else:
                # 完全无法到达，放弃迁徙
                self._migration_states[entity.id] = "settled"
                if logger.isEnabledFor(logging.DEBUG):
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[Migration] E{entity.id} 无法找到可达路径，放弃迁徙")

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

    def _is_walkable_for_animal(
        self, world: World, x: int, y: int, memory: AnimalMemoryComponent
    ) -> bool:
        """
        判断坐标对动物是否可通行。

        优先使用 CollisionSystem 的 is_walkable，
        同时结合记忆中的威胁位置作为额外障碍物。
        """
        # 检查记忆中的威胁位置
        threat_memories = memory.get_memories_by_type("threat")
        for mem in threat_memories:
            if mem.strength > 0.5:
                dist = math.hypot(mem.x - x, mem.y - y)
                if dist < 3.0:  # 避开威胁 3 格范围
                    return False

        # 检查 CollisionSystem（如果有）
        try:
            from space.collision_system import CollisionSystem
            collision_system = world.get_system(CollisionSystem)
            if collision_system:
                return collision_system.is_walkable(world, x, y)
        except Exception as e:
            logger.warning(f"[AnimalMigration] 碰撞检测失败: {e}")

        return True

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

    def _update_migration_component(self, world: World, entity, migration: MigrationComponent,
                                    animal: AnimalComponent, space: SpaceComponent, dt: float) -> None:
        """更新新迁徙组件状态"""
        # 使用静态方法替代组件上的业务方法
        temperature = 15.0  # 简化版，实际应从环境系统获取
        day_length = 12.0

        if migration.is_migrating:
            # 检查是否到达
            if AnimalMigrationSystem.can_arrive(migration, temperature):
                migration.is_migrating = False
                migration.migration_status = "arrived"
                logger.info(f"[Migration] E{entity.id} 到达迁徙目的地")
        else:
            # 检查是否出发
            if AnimalMigrationSystem.should_depart_spring(migration, temperature, day_length):
                migration.is_migrating = True
                migration.migration_status = "migrating"
                migration.migration_season = "spring"
                logger.info(f"[Migration] E{entity.id} 春季迁徙开始")
            elif AnimalMigrationSystem.should_depart_autumn(migration, temperature, day_length):
                migration.is_migrating = True
                migration.migration_status = "migrating"
                migration.migration_season = "autumn"
                logger.info(f"[Migration] E{entity.id} 秋季迁徙开始")

        # 更新迁徙进度
        if migration.is_migrating and migration.destination_x is not None:
            dx = migration.destination_x - space.x
            dy = migration.destination_y - space.y
            dist = math.hypot(dx, dy)
            if dist > 0.1:
                move_dist = min(migration.migration_speed * dt, dist)
                space.x += (dx / dist) * move_dist
                space.y += (dy / dist) * move_dist
                migration.distance_traveled += move_dist
            else:
                # 到达目标
                migration.is_migrating = False
                migration.migration_status = "arrived"
                logger.info(f"[Migration] E{entity.id} 到达目标位置")

    @staticmethod
    def should_depart_spring(migration: MigrationComponent, temperature: float, day_length: float) -> bool:
        """春季出发条件"""
        if not migration.is_migratory:
            return False
        return (temperature >= migration.temperature_threshold_depart and
                day_length >= migration.day_length_trigger and
                migration.energy_reserve >= 0.3)

    @staticmethod
    def should_depart_autumn(migration: MigrationComponent, temperature: float, day_length: float) -> bool:
        """秋季出发条件"""
        if not migration.is_migratory:
            return False
        return (temperature < migration.temperature_threshold_depart and
                day_length < migration.day_length_trigger and
                migration.energy_reserve >= 0.3)

    @staticmethod
    def can_arrive(migration: MigrationComponent, temperature: float) -> bool:
        """到达条件"""
        return temperature >= migration.temperature_threshold_arrive

    def _notify_group_members(
        self, world: World, leader_entity, group_id: int, target
    ) -> None:
        """通知群体成员开始迁徙"""
        for entity, (social) in world.get_components(AnimalSocialComponent):
            if social.group_id == group_id and entity.id != leader_entity.id:
                self._migration_states[entity.id] = "preparing"
                if logger.isEnabledFor(logging.DEBUG):
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[Migration] E{entity.id} 响应领袖迁徙号召")