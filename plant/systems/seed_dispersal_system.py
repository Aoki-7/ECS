#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
植物种子传播系统

提供配置化、环境感知的种子传播策略，取代 BiologyReproductionSystem 中的硬编码方形散布。

传播策略：
    - 圆形散布（自然距离衰减）
    - 土壤适宜性检查（避免落在干旱/岩石区域）
    - 边界检查

与 BiologyReproductionSystem 的关系：
    本系统作为补充层，tick_interval 更大（50），
    负责长距离/策略性传播；BiologyReproductionSystem 继续做基础短距离繁殖。
    若需要完全替代，可在 simulation_loop 中移除 BiologyReproductionSystem。
"""

import math
import random

from core.system import System
from core.world import World
from core.systems.event_log_system import EventLog

from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from space.space_component import SpaceComponent
from environment.soil.components.soil_component import SoilComponent
from biology.ecology.components.speciation_tracker_component import SpeciationTrackerComponent


class SeedDispersalSystem(System):
    tick_interval = 50
    """
    智能种子传播系统

    职责：
        1. 筛选成熟期植物
        2. 检查能量阈值与冷却
        3. 使用圆形分布计算落点
        4. 检查土壤适宜性（避免干旱区域）
        5. 边界检查
        6. 通过 PlantFactory 创建子代
    """

    BASE_ENERGY_THRESHOLD = 25.0
    REPRODUCTION_ENERGY_COST = 0.30
    REPRODUCTION_COOLDOWN_TICKS = 12
    OFFSPRING_ENERGY = 5.0
    MUTATION_RATE = 0.15

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self._tick_counter = 0
        self._last_reproduction: dict[int, int] = {}
        self.enable_log = True

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行种子传播"""
        from core.components.world_config_component import WorldConfigComponent
        world_config = world.get_world_component(WorldConfigComponent)
        self._tick_counter += 1
        soil_cache = self._build_soil_cache(world)
        new_seeds = []

        for entity, (genome, pheno, energy, lifecycle, space) in list(
            world.get_components(
                GenomeComponent,
                PhenotypeComponent,
                EnergyComponent,
                LifeCycleComponent,
                SpaceComponent,
            )
        ):
            seeds = self._generate_seeds_for_entity(
                world, entity, genome, pheno, energy, lifecycle, space, world_config, soil_cache
            )
            new_seeds.extend(seeds)

        self._spawn_offspring(world, new_seeds)

    def _generate_seeds_for_entity(self, world, entity, genome, pheno, energy, lifecycle, space, world_config, soil_cache):
        """为单个实体生成种子位置列表，返回 [(x, y, genome, species, generation), ...]"""
        from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem
        if not LifeCycleSystem.is_mature(lifecycle):
            return []
        if energy.value < self.BASE_ENERGY_THRESHOLD:
            return []

        last_tick = self._last_reproduction.get(entity.id, -self.REPRODUCTION_COOLDOWN_TICKS)
        if self._tick_counter - last_tick < self.REPRODUCTION_COOLDOWN_TICKS:
            return []

        seed_prod = pheno.get("seed_production", 1.0)
        dispersal = pheno.get("dispersal_radius", 3.0)

        energy.value *= (1.0 - self.REPRODUCTION_ENERGY_COST)
        self._last_reproduction[entity.id] = self._tick_counter

        seed_count = max(1, int(seed_prod * self._rng.uniform(0.5, 1.0)))
        seeds = []
        tracker = world.get_component(entity, SpeciationTrackerComponent)
        parent_species = tracker.species_id if tracker else "basic"
        parent_generation = tracker.generation if tracker else 0

        for _ in range(seed_count):
            new_x, new_y = self._compute_dispersal_pos(space, dispersal)
            if not self._is_valid_seed_pos(new_x, new_y, world_config, soil_cache):
                continue
            seeds.append((new_x, new_y, genome, parent_species, parent_generation))

        return seeds

    def _compute_dispersal_pos(self, space, dispersal: float) -> tuple:
        """计算单个种子的散布位置"""
        angle = self._rng.uniform(0, 2.0 * math.pi)
        distance = dispersal * math.sqrt(self._rng.random())
        return int(space.x) + int(distance * math.cos(angle)), int(space.y) + int(distance * math.sin(angle))

    def _is_valid_seed_pos(self, x: int, y: int, world_config, soil_cache: dict) -> bool:
        """检查种子位置是否在边界内且土壤适宜"""
        if not (0 <= x < world_config.map_width and 0 <= y < world_config.map_height):
            return False
        soil = soil_cache.get((x // 10, y // 10))
        if soil is not None and soil.moisture < soil.wilting_point:
            return False
        return True

    def _spawn_offspring(self, world: World, new_seeds: list):
        """批量创建子代实体"""
        from plant.plant_factory import PlantFactory

        for x, y, parent_genome, parent_species, parent_generation in new_seeds:
            child = PlantFactory.create_plant_from_genome(
                world, parent_genome, x, y, variation=self.MUTATION_RATE,
                parent_species=parent_species,
                parent_generation=parent_generation,
            )

            if self.enable_log:
                EventLog.log(
                    world,
                    event_type="seed_dispersal",
                    description=f"植物 E{child.id} 经策略传播落在 ({x},{y})",
                    entity_id=child.id,
                    severity="info",
                )

    # -------------------------------------------------
    # 土壤缓存
    # -------------------------------------------------

    def _build_soil_cache(self, world: World) -> dict:
        cache = {}
        for _, (soil, space) in world.get_components(
            SoilComponent, SpaceComponent
        ):
            # 使用 10x10 网格索引与环境系统对齐
            gx = int(space.x) // 10
            gy = int(space.y) // 10
            cache[(gx, gy)] = soil
        return cache
