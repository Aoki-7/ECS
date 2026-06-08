#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物感知系统

处理动物的感官输入：
    1. 视觉：检测范围内的实体（受昼夜影响）
    2. 听觉：检测声音事件（如捕食者脚步声）
    3. 嗅觉：检测气味标记（如领地气味、食物气味）
    4. 感知融合：综合多感官信息更新 detected_entities

与 AnimalMemorySystem 的关系：
    - 感知到的新实体添加到记忆
    - 记忆中的实体位置用于预测
"""

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from animal.components.animal_perception_component import AnimalPerceptionComponent
from animal.components.animal_memory_component import AnimalMemoryComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem
from plant.components.plant_component import PlantComponent
from biology.lifecycle.components.energy_component import EnergyComponent

import logging

logger = logging.getLogger(__name__)


class AnimalPerceptionSystem(System):
    tick_interval = 8

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新所有动物的感知状态"""
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        # 获取当前时间（用于昼夜判断）
        world_time = getattr(world, 'time', 0)
        is_night = (world_time % 24) < 6 or (world_time % 24) > 20

        for entity, (animal, perception, space) in world.get_components(
            AnimalComponent, AnimalPerceptionComponent, SpaceComponent
        ):
            perception.clear_detection()

            # 视觉感知
            self._visual_perception(
                world, space_system, entity, perception, space, is_night
            )

            # 听觉感知（简化版：检测附近移动实体）
            self._auditory_perception(
                world, space_system, entity, perception, space
            )

            # 嗅觉感知（检测气味标记）
            self._olfactory_perception(
                world, space_system, entity, perception, space
            )

            # 记录到记忆
            self._update_memory(world, entity, perception, space)

            perception.last_perception_tick = getattr(world, '_step_count', 0)

    def _visual_perception(
        self, world: World, space_system: SpaceSystem,
        entity, perception: AnimalPerceptionComponent, space: SpaceComponent,
        is_night: bool
    ) -> None:
        """视觉感知：检测范围内的实体"""
        effective_range = perception.vision_range
        if is_night and not perception.is_night_vision:
            effective_range *= 0.3  # 夜间视觉范围缩减

        nearby = space_system.query_radius(
            x=space.x, y=space.y, r=effective_range
        )

        for candidate_id in nearby:
            if candidate_id == entity.id:
                continue

            candidate = world.query_entity(candidate_id)
            if candidate is None:
                continue

            # 判断实体类型
            entity_type = self._classify_entity(world, candidate)
            if entity_type:
                perception.add_detection(candidate_id, entity_type)

    def _auditory_perception(
        self, world: World, space_system: SpaceSystem,
        entity, perception: AnimalPerceptionComponent, space: SpaceComponent
    ) -> None:
        """听觉感知：检测附近移动/活动实体"""
        nearby = space_system.query_radius(
            x=space.x, y=space.y, r=perception.hearing_range
        )

        for candidate_id in nearby:
            if candidate_id == entity.id:
                continue
            if perception.has_detected(candidate_id):
                continue  # 已视觉检测到

            candidate = world.query_entity(candidate_id)
            if candidate is None:
                continue

            # 检测能量变化（活动迹象）
            energy = world.get_component(candidate, EnergyComponent)
            if energy and hasattr(energy, '_last_change'):
                perception.add_detection(candidate_id, "movement")

    def _olfactory_perception(
        self, world: World, space_system: SpaceSystem,
        entity, perception: AnimalPerceptionComponent, space: SpaceComponent
    ) -> None:
        """嗅觉感知：检测气味标记"""
        from animal.components.animal_territory_component import AnimalTerritoryComponent

        nearby = space_system.query_radius(
            x=space.x, y=space.y, r=perception.smell_range
        )

        for candidate_id in nearby:
            if candidate_id == entity.id:
                continue

            candidate = world.query_entity(candidate_id)
            if candidate is None:
                continue

            territory = world.get_component(candidate, AnimalTerritoryComponent)
            if territory and territory.scent_strength > 0.3:
                perception.add_detection(candidate_id, "scent_mark")

    def _classify_entity(self, world: World, entity) -> str | None:
        """分类实体类型"""
        from animal.components.animal_component import AnimalComponent
        from plant.components.plant_component import PlantComponent
        from resource.components.resource_component import ResourceComponent

        if world.get_component(entity, AnimalComponent):
            return "animal"
        if world.get_component(entity, PlantComponent):
            return "plant"
        if world.get_component(entity, ResourceComponent):
            return "resource"
        return "unknown"

    def _update_memory(
        self, world: World, entity,
        perception: AnimalPerceptionComponent, space: SpaceComponent
    ) -> None:
        """将感知到的实体记录到记忆"""
        memory = world.get_component(entity, AnimalMemoryComponent)
        if memory is None:
            return

        for detected_id, entity_type in perception.detected_entities.items():
            detected = world.query_entity(detected_id)
            if detected is None:
                continue

            detected_space = world.get_component(detected, SpaceComponent)
            if detected_space is None:
                continue

            # 根据类型记录记忆
            memory_type = self._map_to_memory_type(entity_type)
            if memory_type:
                memory.add_memory(
                    detected_space.x, detected_space.y,
                    memory_type, entity_id=detected_id,
                    value=0.5, timestamp=getattr(world, 'time', 0)
                )

    def _map_to_memory_type(self, entity_type: str) -> str | None:
        """映射实体类型到记忆类型"""
        mapping = {
            "animal": "threat",  # 保守策略：动物视为潜在威胁
            "plant": "food",
            "resource": "shelter",
            "scent_mark": "territory",
            "movement": "threat",
        }
        return mapping.get(entity_type)
