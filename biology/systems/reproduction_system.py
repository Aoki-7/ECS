#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:reproduction_system.py
@说明:植物繁殖系统 - 子代继承亲本基因 + 变异
@时间:2026/05/28
@版本:2.2
'''

import random

from core.system import System
from core.world import World
from core.event_log_component import EventLog

from biology.components.energy_component import EnergyComponent
from biology.components.genome_component import GenomeComponent
from biology.components.life_cycle_component import LifeCycleComponent
from biology.components.phenotype_component import PhenotypeComponent
from space.space_component import SpaceComponent
from plant.plant_factory import PlantFactory


class ReproductionSystem(System):
    """
    植物繁殖系统（无性繁殖）

    遗传与变异：
    - 深度复制亲本 Genome
    - 每个基因以 mutation_rate 概率变异
    - 子代基因名保留，值 ±20%

    基因影响：
    - seed_production    → 每次繁殖生成更多/更少子代
    - dispersal_radius   → 子代散布范围
    - metabolism_rate    → 繁殖能量阈值间接影响
    """

    # 繁殖能量阈值基数
    BASE_ENERGY_THRESHOLD = 25.0

    # 繁殖能量消耗比例
    REPRODUCTION_ENERGY_COST = 0.35

    # 繁殖冷却（tick）
    REPRODUCTION_COOLDOWN_TICKS = 7

    # 子代变异率
    REPRODUCTION_MUTATION_RATE = 0.15

    def __init__(self):
        super().__init__()
        self.enable_log = True
        self._last_reproduction: dict[int, int] = {}
        self._tick_counter = 0

    def update(self, world: World, dt: float = 1.0):
        self._tick_counter += 1
        new_seeds = []

        for entity, (genome, pheno, energy, lifecycle, space) in \
                world.get_components(
                    GenomeComponent,
                    PhenotypeComponent,
                    EnergyComponent,
                    LifeCycleComponent,
                    SpaceComponent,
                ):
            # 只在成熟期繁殖
            if not lifecycle.is_mature:
                continue

            # ---- 基因读取 ----
            seed_prod = pheno.get("seed_production", 1.0)
            dispersal = pheno.get("dispersal_radius", 3.0)

            # 能量阈值受 WUE/代谢影响
            energy_threshold = self.BASE_ENERGY_THRESHOLD + (1.0 - pheno.get("water_use_efficiency", 0.05)) * 10.0

            if energy.value < energy_threshold:
                continue

            # 冷却检查
            last_tick = self._last_reproduction.get(entity.id, -self.REPRODUCTION_COOLDOWN_TICKS)
            if self._tick_counter - last_tick < self.REPRODUCTION_COOLDOWN_TICKS:
                continue

            # 消耗能量
            energy.value *= (1.0 - self.REPRODUCTION_ENERGY_COST)
            self._last_reproduction[entity.id] = self._tick_counter

            # ---- 种子数量（由基因决定） ----
            seed_count = max(1, int(seed_prod * random.uniform(0.8, 1.2)))

            for _ in range(seed_count):
                dx = random.randint(-int(dispersal), int(dispersal))
                dy = random.randint(-int(dispersal), int(dispersal))
                new_seeds.append((space.x + dx, space.y + dy, genome))

        # 创建子代
        for x, y, parent_genome in new_seeds:
            child = PlantFactory.create_plant_from_genome(
                world,
                parent_genome=parent_genome,
                x=x,
                y=y,
                variation=self.REPRODUCTION_MUTATION_RATE,
            )
            if self.enable_log:
                EventLog.log(
                    world,
                    event_type="reproduction",
                    description=f"植物 E{child.id} 繁殖于 ({x},{y})",
                    entity_id=child.id,
                    severity="info"
                )
