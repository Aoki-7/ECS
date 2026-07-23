#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/reproduction_system.py
@说明:植物繁殖系统

遍历处于成熟期的植物实体，在满足能量与冷却条件后产生子代。
子代继承亲本基因组（深度复制 + 突变），并在亲本周围随机散布。

基因影响：
    - seed_production  → 每次繁殖生成子代的数量
    - dispersal_radius → 子代散布范围
    - water_use_efficiency → 间接影响繁殖能量阈值
"""

import random

from core.system import System
from core.world import World
from identity.event_log_system import EventLog

from biology.lifecycle.components.energy_component import EnergyComponent
from biology.components.genome_component import GenomeComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem
from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from biology.traits.trait import Trait

from space.space_component import SpaceComponent
from biology.ecology.components.speciation_tracker_component import SpeciationTrackerComponent


class BiologyReproductionSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    植物繁殖系统（无性繁殖）

    核心流程：
        1. 筛选成熟期实体
        2. 检查能量阈值与冷却时间
        3. 消耗能量，计算子代数量
        4. 深度复制 + 突变基因组
        5. 创建子代实体并挂载基础组件
        6. 散布到亲本周围的随机位置
    """

    # 繁殖参数已去硬编码，改为从基因表型动态推导：
    #   - 能量阈值   ← growth_partition（高生长分配=高阈值）
    #   - 能量消耗   ← growth_partition（高生长分配=低消耗）
    #   - 冷却期     ← metabolism_rate（低代谢=长周期）
    #   - 变异率     ← 固定 0.15（遗传学基础）
    #   - 子代能量   ← growth_partition（高生长=高能量储备）

    def __init__(self, seed: int | None = None):
        super().__init__()
        self.enable_log = True
        self._last_reproduction: dict[int, int] = {}
        self._tick_counter = 0
        self._rng = random.Random(seed)

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行繁殖更新"""
        self._tick_counter += 1
        new_seeds = []

        for entity, (genome, pheno, energy, lifecycle, space) in list(world.get_components(
            GenomeComponent, PhenotypeComponent, EnergyComponent, LifeCycleComponent, SpaceComponent
        )):
            seeds = self._generate_seeds_for_entity(world, entity, genome, pheno, energy, lifecycle, space)
            new_seeds.extend(seeds)

        self._spawn_offspring(world, new_seeds)

    def _generate_seeds_for_entity(self, world, entity, genome, pheno, energy, lifecycle, space):
        """为单个实体生成种子，返回种子列表 [(x, y, genome, species, generation), ...]"""
        if not LifeCycleSystem.is_mature(lifecycle):
            return []

        growth = PhenotypeSystem.get(pheno, "growth_partition", 0.4)
        metabolism = PhenotypeSystem.get(pheno, "metabolism_rate", 0.02)
        energy_threshold = 15.0 + growth * 40.0 + (1.0 - PhenotypeSystem.get(pheno, "water_use_efficiency", 0.05)) * 10.0

        if energy.value < energy_threshold:
            return []

        cooldown_ticks = max(2, int(15.0 / (metabolism * 100 + 0.5)))
        last_tick = self._last_reproduction.get(entity.id, -cooldown_ticks)
        if self._tick_counter - last_tick < cooldown_ticks:
            return []

        energy_cost = max(0.1, min(0.5, 0.5 - growth * 0.3))
        energy.value *= (1.0 - energy_cost)
        self._last_reproduction[entity.id] = self._tick_counter

        seed_prod = PhenotypeSystem.get(pheno, "seed_production", 1.0)
        dispersal = PhenotypeSystem.get(pheno, "dispersal_radius", 3.0)
        seed_count = max(1, int(seed_prod * self._rng.uniform(0.8, 1.2)))

        tracker = world.get_component(entity, SpeciationTrackerComponent)
        parent_species = tracker.species_id if tracker else "basic"
        parent_generation = tracker.generation if tracker else 0

        seeds = []
        for _ in range(seed_count):
            dx = self._rng.randint(-int(dispersal), int(dispersal))
            dy = self._rng.randint(-int(dispersal), int(dispersal))
            seeds.append((space.x + dx, space.y + dy, genome, parent_species, parent_generation))
        return seeds

    def _spawn_offspring(self, world: World, new_seeds: list):
        """批量创建子代实体"""
        for x, y, parent_genome, parent_species, parent_generation in new_seeds:
            child = self._create_offspring(
                world, parent_genome, x, y, self.REPRODUCTION_MUTATION_RATE,
                parent_species, parent_generation,
            )
            if self.enable_log:
                EventLog.log(
                    world,
                    event_type="reproduction",
                    description=f"植物 E{child.id} 繁殖于 ({x},{y})",
                    entity_id=child.id,
                    severity="info"
                )

    # -------------------------------------------------
    # 子代创建（内联逻辑，避免硬编码依赖 PlantFactory）
    # -------------------------------------------------

    def _create_offspring(
        self,
        world: World,
        parent_genome: GenomeComponent,
        x: int,
        y: int,
        variation: float,
        parent_species: str = "basic",
        parent_generation: int = 0,
    ):
        """
        基于亲本基因组创建子代实体

        工作流程：
            1. 注册新实体
            2. 深拷贝基因组并施加突变
            3. 挂载完整植物组件（通过 PlantFactory 确保完整性）

        Args:
            world: World 实例
            parent_genome: 亲代基因组
            x: 子代 X 坐标
            y: 子代 Y 坐标
            variation: 突变率

        Returns:
            创建的子代 Entity
        """
        from biology.organisms.plant.plant_factory import PlantFactory

        # 使用 PlantFactory 创建完整植物子代，确保所有生态组件齐全
        return PlantFactory.create_plant_from_genome(
            world=world,
            parent_genome=parent_genome,
            x=x,
            y=y,
            variation=variation,
            parent_species=parent_species,
            parent_generation=parent_generation,
        )