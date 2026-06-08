#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物学习系统

处理动物的行为学习：
    1. 行为-结果关联：记录行为在特定上下文中的结果
    2. 习惯化：重复无害刺激导致反应减弱
    3. 敏感化：强烈负面刺激导致反应增强
    4. 行为选择：基于历史记录选择最佳行为

与 AnimalPerceptionSystem 的关系：
    - 感知到的实体类型构成上下文
    - 感知结果（如发现食物、遭遇捕食者）用于评估行为结果

与 AnimalNeedsSystem 的关系：
    - 需求满足程度作为行为结果的反馈
    - 高需求状态下的行为结果权重更高
"""

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from animal.components.animal_learning_component import AnimalLearningComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from animal.components.animal_perception_component import AnimalPerceptionComponent
from animal.components.animal_memory_component import AnimalMemoryComponent

import logging

logger = logging.getLogger(__name__)


class AnimalLearningSystem(System):
    tick_interval = 15

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新学习状态"""
        for entity, (animal, learning, needs) in world.get_components(
            AnimalComponent, AnimalLearningComponent, AnimalNeedsComponent
        ):
            # 评估最近行为的结果
            self._evaluate_recent_behavior(world, entity, animal, learning, needs)

            # 更新习惯化（对常见刺激）
            self._update_habituations(world, entity, learning)

            # 更新敏感化（对强烈刺激）
            self._update_sensitizations(world, entity, learning, needs)

    def _evaluate_recent_behavior(
        self, world: World, entity, animal: AnimalComponent,
        learning: AnimalLearningComponent, needs: AnimalNeedsComponent
    ) -> None:
        """评估最近行为的结果并记录"""
        perception = world.get_component(entity, AnimalPerceptionComponent)
        if perception is None:
            return

        # 根据需求变化评估行为结果
        context = self._derive_context(perception, needs)

        # 饥饿需求变化
        if needs.hunger < 0.3:
            # 饥饿降低 → 觅食行为成功
            learning.record_behavior("graze", context, 0.8)
        elif needs.hunger > 0.8:
            # 饥饿升高 → 觅食行为失败
            learning.record_behavior("graze", context, -0.5)

        # 恐惧需求变化
        if needs.fear > 0.7:
            # 恐惧升高 → 可能遭遇威胁
            learning.record_behavior("flee", context, 0.6)
            learning.update_sensitization("predator", 0.3)
        elif needs.fear < 0.2:
            # 恐惧降低 → 环境安全
            learning.record_behavior("explore", context, 0.4)

    def _derive_context(
        self, perception: AnimalPerceptionComponent, needs: AnimalNeedsComponent
    ) -> str:
        """从感知和需求推导当前上下文"""
        # 检测威胁
        threats = perception.get_by_type("animal")
        if len(threats) > 0 and needs.fear > 0.5:
            return "near_predator"

        # 检测食物
        food = perception.get_by_type("plant")
        if len(food) > 0:
            return "food_rich"

        # 检测资源
        resources = perception.get_by_type("resource")
        if len(resources) > 0:
            return "resource_available"

        # 默认上下文
        if needs.hunger > 0.7:
            return "food_scarce"
        if needs.thirst > 0.7:
            return "water_scarce"

        return "neutral"

    def _update_habituations(
        self, world: World, entity, learning: AnimalLearningComponent
    ) -> None:
        """更新习惯化程度"""
        perception = world.get_component(entity, AnimalPerceptionComponent)
        if perception is None:
            return

        # 对频繁出现但无害的刺激习惯化
        for entity_id, entity_type in perception.detected_entities.items():
            if entity_type == "plant":
                # 植物是安全的，频繁出现会导致习惯化
                current_count = learning.habituation.get("plant", 0) * 10
                learning.update_habituation("plant", int(current_count) + 1)

    def _update_sensitizations(
        self, world: World, entity,
        learning: AnimalLearningComponent, needs: AnimalNeedsComponent
    ) -> None:
        """更新敏感化程度"""
        # 高恐惧状态增强对威胁的敏感化
        if needs.fear > 0.8:
            learning.update_sensitization("predator", 0.5)
            learning.update_sensitization("danger", 0.3)

        # 自然衰减敏感化
        for stimulus in list(learning.sensitization.keys()):
            learning.sensitization[stimulus] = max(
                0.0, learning.sensitization[stimulus] - 0.01
            )
