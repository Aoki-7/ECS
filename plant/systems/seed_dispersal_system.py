#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
植物种子传播系统

提供配置化、环境感知的种子传播策略，取代 ReproductionSystem 中的硬编码方形散布。

传播策略：
    - 圆形散布（自然距离衰减）
    - 土壤适宜性检查（避免落在干旱/岩石区域）
    - 边界检查

与 ReproductionSystem 的关系：
    本系统作为补充层，tick_interval 更大（50），
    负责长距离/策略性传播；ReproductionSystem 继续做基础短距离繁殖。
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
        """
        执行种子传播

        Args:
            world: World 实例
            dt: 时间步长（预留）
        """
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
            # 只在成熟期传播
            if not lifecycle.is_mature:
                continue

            # 能量阈值
            if energy.value < self.BASE_ENERGY_THRESHOLD:
                continue

            # 冷却检查
            last_tick = self._last_reproduction.get(
                entity.id, -self.REPRODUCTION_COOLDOWN_TICKS
            )
            if self._tick_counter - last_tick < self.REPRODUCTION_COOLDOWN_TICKS:
                continue

            # 读取基因
            seed_prod = pheno.get("seed_production", 1.0)
            dispersal = pheno.get("dispersal_radius", 3.0)

            # 能量消耗
            energy.value *= (1.0 - self.REPRODUCTION_ENERGY_COST)
            self._last_reproduction[entity.id] = self._tick_counter

            # 种子数量
            seed_count = max(1, int(seed_prod * self._rng.uniform(0.5, 1.0)))

            for _ in range(seed_count):
                # 圆形散布（自然距离衰减）
                angle = self._rng.uniform(0, 2.0 * math.pi)
                # 距离偏向近距离，模拟自然种子密度衰减
                distance = dispersal * math.sqrt(self._rng.random())
                dx = int(distance * math.cos(angle))
                dy = int(distance * math.sin(angle))

                new_x = int(space.x) + dx
                new_y = int(space.y) + dy

                # 边界检查（假设地图为 0~99）
                if not (0 <= new_x <= 99 and 0 <= new_y <= 99):
                    continue

                # 土壤适宜性检查
                soil = soil_cache.get((new_x // 10, new_y // 10))
                if soil is not None and soil.moisture < soil.wilting_point:
                    continue  # 太干旱，种子无法存活

                new_seeds.append((new_x, new_y, genome))

        # 创建子代
        for x, y, parent_genome in new_seeds:
            # 延迟导入避免循环依赖
            from plant.plant_factory import PlantFactory

            child = PlantFactory.create_plant_from_genome(
                world, parent_genome, x, y, variation=self.MUTATION_RATE
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
            gx = int(space.x)
            gy = int(space.y)
            cache[(gx, gy)] = soil
        return cache
