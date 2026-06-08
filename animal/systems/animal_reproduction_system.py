#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物繁衍系统

处理动物的繁殖行为：
    1. 扫描所有处于成熟期的动物实体
    2. 检查能量是否达到繁殖阈值
    3. 检查冷却期是否已过
    4. 消耗能量并产生后代

与 Plant 模块的 SeedDispersalSystem 的区别：
    - 动物繁殖不依赖土壤适宜性
    - 后代位置在父母附近小范围偏移
    - 使用 AnimalFactory.create_animal_from_genome() 创建子代
"""

import random

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
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
    """
    动物繁衍系统

    职责：
        1. 遍历所有动物实体
        2. 筛选成熟期 + 高能量 + 冷却期已过的个体
        3. 消耗繁殖能量
        4. 通过基因组产生后代
    """

    # 繁殖参数已去硬编码，改为从基因表型动态推导：
    #   - 能量阈值   ← growth_partition（高生长分配=高阈值，K-策略）
    #   - 能量消耗   ← growth_partition（高生长分配=低消耗，K-策略）
    #   - 冷却期     ← metabolism_rate（低代谢=长周期，类似大型哺乳动物）

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self._tick_counter = 0
        self._last_reproduction: dict[int, int] = {}

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行动物繁衍更新

        Args:
            world: World 实例
            dt: 时间步长（预留）
        """
        self._tick_counter += 1

        for entity, (animal, energy, lifecycle, genome, space) in list(
            world.get_components(
                AnimalComponent,
                EnergyComponent,
                LifeCycleComponent,
                GenomeComponent,
                SpaceComponent,
            )
        ):
            # 只在成熟期繁殖
            if not lifecycle.is_mature:
                continue

            # ── 动态推导繁殖参数 ──
            pheno = world.get_component(entity, PhenotypeComponent)
            growth = pheno.get("growth_partition", 0.4) if pheno else 0.4
            metabolism = pheno.get("metabolism_rate", 0.02) if pheno else 0.02

            # 能量阈值：高生长分配 = 高阈值（优先投资自身，类似 K-策略）
            energy_threshold = 20.0 + growth * 60.0

            # 冷却期：低代谢 = 长周期（类似大型哺乳动物，r-策略 vs K-策略）
            cooldown_ticks = max(3, int(30.0 / (metabolism * 100 + 0.5)))

            # 能量消耗：高生长分配 = 低消耗（K-策略：少量高质量后代）
            energy_cost = max(0.1, min(0.5, 0.5 - growth * 0.3))

            # 能量阈值检查
            if energy.value < energy_threshold:
                continue

            # 冷却期检查
            last_tick = self._last_reproduction.get(entity.id, -cooldown_ticks)
            if self._tick_counter - last_tick < cooldown_ticks:
                continue

            # 能量消耗
            energy.value *= (1.0 - energy_cost)
            self._last_reproduction[entity.id] = self._tick_counter

            # 计算后代位置（父母附近随机偏移 1~2 格）
            child_x = space.x + self._rng.randint(-2, 2)
            child_y = space.y + self._rng.randint(-2, 2)

            # 边界保护：确保坐标非负
            child_x = max(0, child_x)
            child_y = max(0, child_y)

            # 产生后代（继承父母的物种标识和代数）
            from biology.ecology.components.speciation_tracker_component import SpeciationTrackerComponent
            parent_tracker = world.get_component(entity, SpeciationTrackerComponent)
            parent_species = animal.species
            parent_generation = parent_tracker.generation if parent_tracker else 0

            child = AnimalFactory.create_animal_from_genome(
                world, genome, x=child_x, y=child_y,
                parent_species=parent_species,
                parent_generation=parent_generation,
            )

            logger.debug(
                f"[AnimalReproduction] E{entity.id}({animal.species}) "
                f"产生后代 E{child.id} at ({child_x}, {child_y})"
            )
