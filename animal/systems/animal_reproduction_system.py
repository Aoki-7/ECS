#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物繁衍系统（重构版）

处理动物的繁殖行为：
    1. 扫描所有处于成熟期的动物实体
    2. 检查能量是否达到繁殖阈值
    3. 检查冷却期是否已过（使用 ReproductionComponent 替代 dict）
    4. 消耗能量并产生后代
    5. 支持怀孕机制（雌性怀孕 → 分娩）

与 AnimalSocialSystem 的关系：
    - SocialSystem 负责配对（设置 mate_id）
    - ReproductionSystem 在配对成功后执行繁殖
"""

import random

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from animal.components.animal_reproduction_component import AnimalReproductionComponent
from animal.components.animal_social_component import AnimalSocialComponent
from animal.animal_factory import AnimalFactory
from biology.components.genome_component import GenomeComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from space.space_component import SpaceComponent
from biology.components.phenotype_component import PhenotypeComponent

import logging

logger = logging.getLogger(__name__)


class AnimalReproductionSystem(System):
    tick_interval = 20

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self._tick_counter = 0

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行动物繁衍更新"""
        self._tick_counter += 1

        for entity, (animal, repro, energy, lifecycle, genome, space) in list(
            world.get_components(
                AnimalComponent,
                AnimalReproductionComponent,
                EnergyComponent,
                LifeCycleComponent,
                GenomeComponent,
                SpaceComponent,
            )
        ):
            from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem
            if not LifeCycleSystem.is_mature(lifecycle):
                continue

            # 处理怀孕分娩
            if repro.is_pregnant and animal.gender == "female":
                if repro.check_birth_ready(self._tick_counter):
                    self._give_birth(world, entity, animal, repro, genome, space)
                continue

            # 检查是否可繁殖
            if not self._can_reproduce(entity, repro, energy):
                continue

            # 获取配偶
            mate_id = self._get_mate_id(world, entity, animal, repro)
            if mate_id is None:
                continue

            # 执行繁殖
            self._reproduce(world, entity, animal, repro, energy, genome, space, mate_id)

    def _can_reproduce(
        self, entity, repro: AnimalReproductionComponent, energy: EnergyComponent
    ) -> bool:
        """检查繁殖条件：冷却期 + 能量阈值"""
        if not repro.is_ready(self._tick_counter):
            return False

        # 能量阈值：至少 30% 最大能量
        threshold = getattr(energy, "max_energy", 100.0) * 0.3
        return energy.value >= threshold

    def _get_mate_id(
        self, world: World, entity, animal: AnimalComponent, repro: AnimalReproductionComponent
    ) -> int | None:
        """获取配偶 ID：优先使用社交组件中的配偶"""
        # 从 AnimalSocialComponent 获取（社交系统负责配对）
        social = world.get_component(entity, AnimalSocialComponent)
        if social and social.mate_id != -1:
            mate = world.query_entity(social.mate_id)
            if mate is not None:
                # 验证配偶是否为异性且成熟
                mate_animal = world.get_component(mate, AnimalComponent)
                if mate_animal and mate_animal.gender != animal.gender:
                    return social.mate_id

        # 从 ReproductionComponent 获取（备用）
        if repro.mate_id != -1:
            mate = world.query_entity(repro.mate_id)
            if mate is not None:
                return repro.mate_id

        return None

    def _reproduce(
        self, world: World, entity, animal: AnimalComponent,
        repro: AnimalReproductionComponent, energy: EnergyComponent,
        genome: GenomeComponent, space: SpaceComponent, mate_id: int
    ) -> None:
        """执行繁殖逻辑"""
        # 动态推导繁殖参数
        pheno = world.get_component(entity, PhenotypeComponent)
        growth = pheno.get("growth_partition", 0.4) if pheno else 0.4
        metabolism = pheno.get("metabolism_rate", 0.02) if pheno else 0.02

        # 能量消耗
        energy_cost = max(0.1, min(0.5, 0.5 - growth * 0.3))
        energy.value *= (1.0 - energy_cost)

        # 更新冷却期
        repro.cooldown_ticks = max(3, int(30.0 / (metabolism * 100 + 0.5)))
        repro.record_reproduction(self._tick_counter)

        if animal.gender == "female":
            # 雌性进入怀孕状态
            repro.start_pregnancy(self._tick_counter, mate_id)
            logger.debug(
                f"[Reproduction] E{entity.id}({animal.species}) 怀孕，"
                f"配偶 E{mate_id}，冷却期 {repro.cooldown_ticks} ticks"
            )
        else:
            # 雄性直接记录（实际繁殖由雌性执行）
            logger.debug(
                f"[Reproduction] E{entity.id}({animal.species}) 与 E{mate_id} 配对"
            )

    def _give_birth(
        self, world: World, entity, animal: AnimalComponent,
        repro: AnimalReproductionComponent, genome: GenomeComponent, space: SpaceComponent
    ) -> None:
        """分娩产生后代"""
        # 计算后代位置
        child_x = max(0, space.x + self._rng.randint(-2, 2))
        child_y = max(0, space.y + self._rng.randint(-2, 2))

        # 创建后代
        child = AnimalFactory.create_animal_from_genome(
            world, genome, x=child_x, y=child_y,
            parent_species=animal.species,
            parent_generation=repro.reproduction_count,
        )

        # 更新父母状态
        repro.give_birth()

        # 记录到社交组件
        social = world.get_component(entity, AnimalSocialComponent)
        if social:
            social.add_offspring(child.id)

        logger.info(
            f"[Reproduction] E{entity.id}({animal.species}) 分娩，"
            f"后代 E{child.id} at ({child_x}, {child_y})"
        )
