# plant/plant_factory.py
"""
植物实体工厂模块

提供基于物种预设模板创建植物 Entity 的工厂方法，
支持单个体创建以及基于亲代基因组的无性繁殖。
"""

import random
from typing import Dict, List, Optional

from core.entity import Entity
from core.world import World

from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.components.energy_component import EnergyComponent
from biology.components.morphology_component import MorphologyComponent
from biology.components.life_cycle_component import LifeCycleComponent
from biology.components.immune_component import ImmuneComponent
from biology.components.health_status_component import HealthStatusComponent
from biology.components.nutrient_component import NutrientComponent

from biology.genetics.gene import Gene

from space.space_component import SpaceComponent

from .presets import SPECIES_PRESETS, SPECIES_LIFECYCLE

__all__ = ["PlantFactory"]


class PlantFactory:
    """
    通用植物工厂

    职责：
        1. 根据物种预设 (SPECIES_PRESETS) 创建 Entity；
        2. 为每个基因引入个体差异（变异）；
        3. 自动挂载植物生存所需的基础生物学组件（含生命周期与空间坐标）；
        4. 将实体注册到 World 中。

    核心流程：
        create_plant() -> _build_genome() -> _init_lifecycle() -> _attach_base_components()

    基因维度（按功能分类）：
        ─ 光合系统：max_photosynthesis_rate, light_use_efficiency, shade_tolerance
        ─ 温度响应：optimal_temp, cold_tolerance, heat_tolerance
        ─ 水分利用：water_use_efficiency
        ─ 代谢分配：metabolism_rate, growth_partition
        ─ 形态分配：leaf_bias, root_bias, stem_bias, max_height, stem_thickness_factor
        ─ 繁殖策略：seed_production, dispersal_radius
    """

    # 直接引用外部预设表，支持运行时被替换或热更新
    SPECIES_PRESETS = SPECIES_PRESETS
    SPECIES_LIFECYCLE = SPECIES_LIFECYCLE

    # -------------------------------------------------
    # 主入口：创建植物实体
    # -------------------------------------------------

    @classmethod
    def create_plant(
        cls,
        world: World,
        species: str = "basic",
        variation: float = 0.1,
        seed: Optional[int] = None,
        x: int = 0,
        y: int = 0,
    ) -> Entity:
        """
        创建完整植物 Entity，并自动注册到 world

        Args:
            world: World 实例，负责实体生命周期管理。
            species: 物种标识名，必须是 SPECIES_PRESETS 的键之一。
            variation: 变异系数 [0, +∞)。0 表示无个体差异，越大差异越明显。
            seed: 可选的随机数种子，用于可复现的个体生成。
            x: 空间 X 坐标。
            y: 空间 Y 坐标。

        Returns:
            创建并挂载好组件的 Entity 对象（含 16 个基因 + 6 个组件）。

        Raises:
            ValueError: 传入未知物种 或 variation < 0。
        """
        # 初始化局部随机数生成器，避免污染全局 random 状态
        rng = random.Random(seed) if seed is not None else random

        # 校验物种有效性
        if species not in cls.SPECIES_PRESETS:
            available = list(cls.SPECIES_PRESETS.keys())
            raise ValueError(
                f"Unknown species: '{species}'. "
                f"Available species: {available}"
            )

        # 校验变异系数非负
        if variation < 0:
            raise ValueError(
                f"variation must be >= 0, got {variation}"
            )

        # 获取该物种的基因基础模板
        preset = cls.SPECIES_PRESETS[species]

        # ---- Step 1: 在 world 中注册新实体 ----
        entity = world.create_entity()

        # ---- Step 2: 根据模板构建带变异的基因组 ----
        genome = cls._build_genome(preset, species, variation, rng)

        # ---- Step 3: 初始化生命周期组件 ----
        lifecycle = cls._init_lifecycle(species)

        # ---- Step 4: 挂载植物基础组件 ----
        cls._attach_base_components(world, entity, genome, lifecycle, x, y)

        return entity

    # -------------------------------------------------
    # 批量创建
    # -------------------------------------------------

    @classmethod
    def create_batch(
        cls,
        world: World,
        count: int,
        species: str = "basic",
        variation: float = 0.1,
        seed: Optional[int] = None,
        x: int = 0,
        y: int = 0,
    ) -> List[Entity]:
        """
        批量创建植物实体

        内部为每个实体分配独立的随机子序列，确保即使传入同一个种子，
        不同批次或不同个体之间也不会产生意外的随机耦合。

        Args:
            world: World 实例。
            count: 需要创建的数量 (>0)。
            species: 物种标识名。
            variation: 变异系数。
            seed: 可选的随机数种子，控制整批的随机性。
            x: 空间 X 坐标。
            y: 空间 Y 坐标。

        Returns:
            按创建顺序排列的 Entity 列表。
        """
        rng = random.Random(seed) if seed is not None else random
        entities: List[Entity] = []

        for _ in range(count):
            # 每个实体使用独立的随机种子，避免序列冲突
            entity_seed = rng.randint(0, 2**31 - 1)
            entity = cls.create_plant(world, species, variation, entity_seed, x, y)
            entities.append(entity)

        return entities

    # -------------------------------------------------
    # 基于亲代基因组创建子代（繁殖）
    # -------------------------------------------------

    @classmethod
    def create_plant_from_genome(
        cls,
        world: World,
        parent_genome: GenomeComponent,
        x: int = 0,
        y: int = 0,
        variation: float = 0.15,
    ) -> Entity:
        """
        基于亲本 Genome 创建子代（无性繁殖 + 变异）

        工作流程：
            1. 复制亲代基因组（深拷贝所有 Gene）；
            2. 对复制后的基因组施加突变；
            3. 以种子阶段初始化生命周期；
            4. 挂载基础组件并完成 world 注册。

        注意：
            子代初始能量设为 5.0（低于 create_plant 的 10.0），
            模拟种子阶段能量储备较少的状态。

        Args:
            world: World 实例。
            parent_genome: 亲代的 GenomeComponent，提供完整的基因蓝本。
            x: 子代空间 X 坐标。
            y: 子代空间 Y 坐标。
            variation: 突变率，作为 mutation_rate 传入 GenomeComponent.mutate()。

        Returns:
            携带遗传与变异基因的新 Entity。
        """
        # 在 world 中注册新实体
        entity = world.create_entity()

        # 深拷贝基因组并进行突变，产生子代基因型
        child_genome = parent_genome.copy()
        child_genome.mutate(mutation_rate=variation)

        # 子代以种子阶段开始生命周期
        lifecycle = LifeCycleComponent(stage=LifeCycleComponent.SEED)

        # 挂载基础组件（子代能量较低，模拟种子状态）
        cls._attach_base_components(
            world, entity, child_genome, lifecycle, x, y, energy_value=5.0
        )

        return entity

    # -------------------------------------------------
    # 内部辅助方法
    # -------------------------------------------------

    @classmethod
    def _build_genome(
        cls,
        preset: Dict[str, float],
        species: str,
        variation: float,
        rng: random.Random,
    ) -> GenomeComponent:
        """
        根据物种预设构建带变异的基因组

        变异算法：
            actual_value = uniform(
                base_value * (1 - variation),
                base_value * (1 + variation)
            )

        Args:
            preset: 物种基因模板，{expression_target: base_value}。
            species: 物种标识名，用于生成基因名前缀。
            variation: 变异系数。
            rng: 局部随机数生成器实例。

        Returns:
            组装完成的 GenomeComponent。
        """
        genome = GenomeComponent()

        for trait_name, base_value in preset.items():
            # 计算该基因允许浮动的范围
            delta = base_value * variation
            actual_value = rng.uniform(
                base_value - delta,
                base_value + delta
            )

            # 构建基因：name 用于调试和日志，expression_target 用于表型映射
            genome.add_gene(
                Gene(
                    name=f"{species.upper()}_{trait_name.upper()}",
                    expression_target=trait_name,
                    strength=actual_value,
                )
            )

        return genome

    @classmethod
    def _init_lifecycle(cls, species: str) -> LifeCycleComponent:
        """
        根据物种生命周期预设初始化 LifeCycleComponent

        Args:
            species: 物种标识名。

        Returns:
            配置好的 LifeCycleComponent（阶段为 SEED）。
        """
        lc_config = cls.SPECIES_LIFECYCLE.get(
            species, cls.SPECIES_LIFECYCLE["basic"]
        )

        return LifeCycleComponent(
            stage=LifeCycleComponent.SEED,
            max_age=lc_config["max_age"],
            stage_durations=lc_config["stage_durations"],
            gdd_requirements=lc_config["gdd_requirements"],
        )

    @classmethod
    def _attach_base_components(
        cls,
        world: World,
        entity: Entity,
        genome: GenomeComponent,
        lifecycle: LifeCycleComponent,
        x: int,
        y: int,
        energy_value: float = 10.0,
    ) -> None:
        """
        为实体挂载植物生存必需的基础生物学组件

        挂载顺序：
            1. GenomeComponent      — 基因型（可遗传信息）
            2. PhenotypeComponent   — 表型容器（运行时特征计算结果）
            3. EnergyComponent      — 能量储备
            4. MorphologyComponent  — 形态外观（渲染与物理碰撞相关）
            5. LifeCycleComponent   — 生命周期（阶段推进与衰老管理）
            6. SpaceComponent       — 空间坐标（x, y, layer=0）

        Args:
            world: World 实例。
            entity: 目标实体。
            genome: 已构建好的基因组组件。
            lifecycle: 已初始化的生命周期组件。
            x: 空间 X 坐标。
            y: 空间 Y 坐标。
            energy_value: 初始能量值（默认 10.0，子代可设为 5.0）。
        """
        # 基因型：决定个体的可遗传特征
        world.add_component(entity, genome)

        # 表型：运行时由基因表达系统填充
        world.add_component(entity, PhenotypeComponent())

        # 能量：提供发芽前的基础消耗
        initial_energy = EnergyComponent()
        initial_energy.value = energy_value
        world.add_component(entity, initial_energy)

        # 形态：默认参数由 MorphologyComponent 的 dataclass 提供
        world.add_component(entity, MorphologyComponent())

        # 生命周期：管理从种子到死亡的各阶段推进
        world.add_component(entity, lifecycle)

        # 空间：固定在指定二维坐标，layer=0 表示地面层
        world.add_component(entity, SpaceComponent(x=x, y=y, layer=0))

        # 扩展生物学组件：免疫、损伤、营养、竞争
        world.add_component(entity, ImmuneComponent())
        world.add_component(entity, HealthStatusComponent())
        world.add_component(entity, NutrientComponent())
