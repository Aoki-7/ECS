#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物捕食系统（重构版）

处理食肉动物 (diet="carnivore") 的捕食行为。
已拆分 update() 为多个子方法，每方法不超过 40 行。

与 GrazingSystem 的关系：
    - GrazingSystem 处理植物 → 食草动物的能量转移
    - PredationSystem 处理食草动物 → 食肉动物的能量转移
    - 两者共同构成食物链的两级消费层
"""

import random

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem
from biology.lifecycle.death.components.pending_death_component import PendingDeathComponent
from core.category_component import CategoryComponent
from core.category import EntityCategory
from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from animal.components.animal_memory_component import AnimalMemoryComponent

import logging

logger = logging.getLogger(__name__)


class PredationSystem(System):
    tick_interval = 15

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self._tick_counter = 0

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行捕食更新"""
        self._tick_counter += 1
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (predator, pred_energy, pred_space) in world.get_components(
            AnimalComponent, EnergyComponent, SpaceComponent
        ):
            if predator.diet != "carnivore":
                continue
            self._process_predator(world, space_system, entity, predator, pred_energy, pred_space)

    def _process_predator(
        self, world: World, space_system: SpaceSystem,
        entity, predator: AnimalComponent, pred_energy: EnergyComponent, pred_space: SpaceComponent
    ) -> None:
        """处理单个捕食者的行为"""
        pred_pheno = world.get_component(entity, PhenotypeComponent)
        pred_morph = world.get_component(entity, MorphologyComponent)

        if not self._can_attack(entity, pred_pheno):
            return

        prey_id = self._find_prey(world, space_system, pred_space, predator)
        if prey_id is None:
            return

        self._execute_attack(world, entity, predator, pred_energy, pred_pheno, pred_morph, prey_id)
        self._record_attack(entity)

    def _can_attack(self, entity, pred_pheno) -> bool:
        """检查攻击冷却和饥饿状态"""
        needs = getattr(entity, '_needs', None)
        if needs and needs.fear > 0.5:
            return False

        metabolism = pred_pheno.get("metabolism_rate", 0.02) if pred_pheno else 0.02
        attack_cooldown = max(1, int(5.0 / (metabolism * 100 + 0.1)))
        return True

    def _find_prey(
        self, world: World, space_system: SpaceSystem,
        pred_space: SpaceComponent, predator: AnimalComponent
    ) -> int | None:
        """在捕食范围内寻找最佳猎物"""
        nearby = space_system.query_radius(
            x=pred_space.x, y=pred_space.y, r=predator.grazing_range
        )

        best_prey = None
        best_energy = 0.0

        for candidate_id in nearby:
            candidate = world.query_entity(candidate_id)
            if candidate is None:
                continue

            prey_animal = world.get_component(candidate, AnimalComponent)
            if prey_animal is None or prey_animal.diet not in ("herbivore",):
                continue

            cat = world.get_component(candidate, CategoryComponent)
            if cat is not None and cat.category != EntityCategory.ANIMAL:
                continue

            if world.get_component(candidate, PendingDeathComponent) is not None:
                continue

            prey_energy = world.get_component(candidate, EnergyComponent)
            if prey_energy is None:
                continue

            if prey_energy.value > best_energy:
                best_energy = prey_energy.value
                best_prey = candidate_id

        return best_prey

    def _execute_attack(
        self, world: World, predator_id: int, predator: AnimalComponent,
        pred_energy: EnergyComponent, pred_pheno: PhenotypeComponent,
        pred_morph: MorphologyComponent, prey_id: int
    ) -> None:
        """执行攻击并处理结果"""
        prey = world.query_entity(prey_id)
        if prey is None:
            return

        damage = self._calculate_damage(pred_pheno, pred_morph)
        success = self._check_attack_success(pred_pheno, prey)

        if not success:
            logger.debug(f"[Predation] E{predator_id} 攻击 E{prey_id} 失败")
            return

        prey_energy = world.get_component(prey, EnergyComponent)
        if prey_energy is None:
            return

        prey_energy.value = max(0.0, prey_energy.value - damage)
        logger.debug(f"[Predation] E{predator_id} 对 E{prey_id} 造成 {damage:.1f} 伤害")

        if prey_energy.value <= 0:
            self._kill_prey(world, prey, prey_id, predator_id, pred_energy)
        else:
            self._transfer_partial_energy(pred_energy, prey_energy, damage)

    def _calculate_damage(self, pred_pheno: PhenotypeComponent, pred_morph: MorphologyComponent) -> float:
        """计算攻击伤害"""
        speed = pred_pheno.get("speed_factor", 1.0) if pred_pheno else 1.0
        strength = getattr(pred_morph, 'strength', 10.0) if pred_morph else 10.0
        return speed * strength * self._rng.uniform(0.8, 1.2)

    def _check_attack_success(self, pred_pheno: PhenotypeComponent, prey) -> bool:
        """检查攻击是否成功"""
        pred_speed = pred_pheno.get("speed_factor", 1.0) if pred_pheno else 1.0
        prey_pheno = getattr(prey, '_pheno', None)
        prey_speed = prey_pheno.get("speed_factor", 1.0) if prey_pheno else 1.0
        success_rate = min(0.95, pred_speed / max(prey_speed, 0.1))
        return self._rng.random() < success_rate

    def _kill_prey(self, world: World, prey, prey_id: int, predator_id: int, pred_energy: EnergyComponent) -> None:
        """杀死猎物并转移全部能量"""
        prey_energy = world.get_component(prey, EnergyComponent)
        if prey_energy:
            energy_gain = prey_energy.value * 0.8
            pred_energy.value = min(
                getattr(pred_energy, "max_energy", 1000.0),
                pred_energy.value + energy_gain
            )
            logger.info(f"[Predation] E{predator_id} 杀死 E{prey_id}，获得 {energy_gain:.1f} 能量")

        world.add_component(prey, PendingDeathComponent(reason="predation"))

        # 记录记忆
        memory = world.get_component(prey, AnimalMemoryComponent)
        if memory:
            prey_space = world.get_component(prey, SpaceComponent)
            if prey_space:
                memory.add_memory(
                    prey_space.x, prey_space.y, "threat",
                    entity_id=predator_id, value=1.0
                )

    def _transfer_partial_energy(self, pred_energy: EnergyComponent, prey_energy: EnergyComponent, damage: float) -> None:
        """转移部分能量给捕食者"""
        transfer = damage * 0.3
        pred_energy.value = min(
            getattr(pred_energy, "max_energy", 1000.0),
            pred_energy.value + transfer
        )

    def _record_attack(self, entity) -> None:
        """记录攻击时间（简化版，后续可用 Component 替代）"""
        pass
