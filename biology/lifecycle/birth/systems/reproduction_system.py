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
from core.systems.event_log_system import EventLog

from biology.lifecycle.components.energy_component import EnergyComponent
from biology.components.genome_component import GenomeComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from biology.traits.trait import Trait

from space.space_component import SpaceComponent


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

    # 繁殖能量阈值基数
    BASE_ENERGY_THRESHOLD = 25.0

    # 繁殖能量消耗比例
    REPRODUCTION_ENERGY_COST = 0.35

    # 繁殖冷却（tick）
    REPRODUCTION_COOLDOWN_TICKS = 7

    # 子代变异率
    REPRODUCTION_MUTATION_RATE = 0.15

    # 子代初始能量（模拟种子状态）
    OFFSPRING_ENERGY = 5.0

    def __init__(self, seed: int | None = None):
        super().__init__()
        self.enable_log = True
        self._last_reproduction: dict[int, int] = {}
        self._tick_counter = 0
        self._rng = random.Random(seed)

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行繁殖更新

        Args:
            world: World 实例
            dt: 时间步长（当前模型以 tick 为单位，预留参数）
        """
        self._tick_counter += 1
        new_seeds = []

        for entity, (genome, pheno, energy, lifecycle, space) in \
                list(world.get_components(
                    GenomeComponent,
                    PhenotypeComponent,
                    EnergyComponent,
                    LifeCycleComponent,
                    SpaceComponent,
                )):
            # 只在成熟期繁殖
            if not lifecycle.is_mature:
                continue

            # ---- 基因读取 ----
            seed_prod = pheno.get("seed_production", 1.0)
            dispersal = pheno.get("dispersal_radius", 3.0)

            # 能量阈值受 WUE/代谢影响
            energy_threshold = (
                self.BASE_ENERGY_THRESHOLD
                + (1.0 - pheno.get("water_use_efficiency", 0.05)) * 10.0
            )

            if energy.value < energy_threshold:
                continue

            # 冷却检查
            last_tick = self._last_reproduction.get(
                entity.id, -self.REPRODUCTION_COOLDOWN_TICKS
            )
            if self._tick_counter - last_tick < self.REPRODUCTION_COOLDOWN_TICKS:
                continue

            # 消耗能量
            energy.value *= (1.0 - self.REPRODUCTION_ENERGY_COST)
            self._last_reproduction[entity.id] = self._tick_counter

            # ---- 种子数量（由基因决定，带随机波动） ----
            seed_count = max(1, int(seed_prod * self._rng.uniform(0.8, 1.2)))

            for _ in range(seed_count):
                dx = self._rng.randint(-int(dispersal), int(dispersal))
                dy = self._rng.randint(-int(dispersal), int(dispersal))
                new_seeds.append((space.x + dx, space.y + dy, genome))

        # 创建子代
        for x, y, parent_genome in new_seeds:
            child = self._create_offspring(
                world, parent_genome, x, y, self.REPRODUCTION_MUTATION_RATE
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
    ):
        """
        基于亲本基因组创建子代实体

        工作流程：
            1. 注册新实体
            2. 深拷贝基因组并施加突变
            3. 挂载基础组件（基因型、表型、能量、形态、生命周期、空间）

        Args:
            world: World 实例
            parent_genome: 亲代基因组
            x: 子代 X 坐标
            y: 子代 Y 坐标
            variation: 突变率

        Returns:
            创建的子代 Entity
        """
        entity = world.create_entity()

        # 遗传 + 变异
        child_genome = parent_genome.copy()
        child_genome.mutate(mutation_rate=variation)

        # 基因型
        world.add_component(entity, child_genome)

        # 表型容器
        world.add_component(entity, PhenotypeComponent())

        # 能量（种子状态，初始值较低）
        init_energy = EnergyComponent()
        init_energy.value = self.OFFSPRING_ENERGY
        world.add_component(entity, init_energy)

        # 形态
        world.add_component(entity, MorphologyComponent())

        # 生命周期（从种子开始）
        lifecycle = LifeCycleComponent(stage=LifeCycleComponent.SEED)
        world.add_component(entity, lifecycle)

        # 空间坐标
        world.add_component(entity, SpaceComponent(x=x, y=y, layer=0))

        return entity
