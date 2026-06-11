# animal/animal_factory.py
"""
动物实体工厂模块

提供基于物种预设模板创建动物 Entity 的工厂方法，
支持单个体创建、批量创建以及基于亲代基因组的繁殖。
"""

import random
from typing import Dict, List, Optional

from core.entity import Entity
from core.world import World

from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.components.immune_component import ImmuneComponent
from biology.components.health_status_component import HealthStatusComponent
from biology.genetics.gene import Gene
from space.space_component import SpaceComponent

from biology.ecology.components.food_chain_component import FoodChainComponent
from biology.ecology.components.population_component import PopulationComponent
from biology.ecology.components.speciation_tracker_component import SpeciationTrackerComponent
from identity.category_component import CategoryComponent
from identity.category import EntityCategory
from identity.subcategory import AnimalSubCategory

from .presets import SPECIES_PRESETS

__all__ = ["AnimalFactory"]


class AnimalFactory:
    """
    通用动物工厂

    职责：
        1. 根据物种预设 (SPECIES_PRESETS) 创建 Entity；
        2. 为每个基因引入个体差异（变异）；
        3. 自动挂载动物生存所需的基础生物学组件；
        4. 将实体注册到 World 中。

    核心流程：
        create_animal() -> _build_genome() -> _attach_base_components()
    """

    # 直接引用外部预设表，支持运行时被替换或热更新
    SPECIES_PRESETS = SPECIES_PRESETS

    # -------------------------------------------------
    # 主入口：创建动物实体
    # -------------------------------------------------

    @classmethod
    def create_animal(
        cls,
        world: World,
        species: str = "basic",
        variation: float = 0.1,
        seed: Optional[int] = None,
        x: int = 0,
        y: int = 0,
    ) -> Entity:
        """
        创建完整动物 Entity，并自动注册到 world

        Args:
            world: World 实例，负责实体生命周期管理。
            species: 物种标识名，必须是 SPECIES_PRESETS 的键之一。
            variation: 变异系数 [0, +∞)。0 表示无个体差异，越大差异越明显。
            seed: 可选的随机数种子，用于可复现的个体生成。
            x: 空间 X 坐标。
            y: 空间 Y 坐标。

        Returns:
            创建并挂载好组件的 Entity 对象。

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

        # ---- Step 3: 初始化生命周期 ----
        lifecycle = cls._init_lifecycle(preset)

        # ---- Step 4: 挂载动物生存必需的基础组件 ----
        cls._attach_base_components(world, entity, genome, lifecycle, preset, species, x, y)

        # ---- Step 5: 挂载物种形成追踪组件 ----
        world.add_component(entity, SpeciationTrackerComponent(
            species_id=species,
            original_species=species,
            generation=0,
            lineage_id=f"{species}_{entity.id}",
        ))

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
    ) -> List[Entity]:
        """
        批量创建动物实体

        内部为每个实体分配独立的随机子序列，确保即使传入同一个种子，
        不同批次或不同个体之间也不会产生意外的随机耦合。

        Args:
            world: World 实例。
            count: 需要创建的数量 (>0)。
            species: 物种标识名。
            variation: 变异系数。
            seed: 可选的随机数种子，控制整批的随机性。

        Returns:
            按创建顺序排列的 Entity 列表。
        """
        rng = random.Random(seed) if seed is not None else random
        entities: List[Entity] = []

        for _ in range(count):
            # 每个实体使用独立的随机种子，避免序列冲突
            entity_seed = rng.randint(0, 2**31 - 1)
            entity = cls.create_animal(world, species, variation, entity_seed)
            entities.append(entity)

        return entities

    # -------------------------------------------------
    # 基于亲代基因组创建子代（繁殖）
    # -------------------------------------------------

    @classmethod
    def create_animal_from_genome(
        cls,
        world: World,
        parent_genome: GenomeComponent,
        variation: float = 0.15,
        x: int = 0,
        y: int = 0,
        parent_species: str = "basic",
        parent_generation: int = 0,
    ) -> Entity:
        """
        基于亲本 Genome 创建子代（遗传 + 变异）

        工作流程：
            1. 复制亲代基因组（深拷贝所有 Gene）；
            2. 对复制后的基因组施加突变；
            3. 挂载基础组件并完成 world 注册。

        Args:
            world: World 实例。
            parent_genome: 亲代的 GenomeComponent，提供完整的基因蓝本。
            variation: 突变率，作为 mutation_rate 传入 GenomeComponent.mutate()。
            x: 子代空间 X 坐标。
            y: 子代空间 Y 坐标。

        Returns:
            携带遗传与变异基因的新 Entity。
        """
        # 在 world 中注册新实体
        entity = world.create_entity()

        # 深拷贝基因组并进行突变，产生子代基因型
        child_genome = parent_genome.copy()
        child_genome.mutate(mutation_rate=variation)

        # 子代以幼体阶段开始
        lifecycle = LifeCycleComponent(
            stage=LifeCycleComponent.SEED,
            stage_durations=[48.0, 168.0, 720.0, 4320.0, 720.0],
            max_age=8760.0,
        )

        # 挂载基础组件（子代使用 basic 物种预设）
        cls._attach_base_components(
            world, entity, child_genome, lifecycle, cls.SPECIES_PRESETS["basic"], parent_species, x, y
        )

        # 挂载物种形成追踪组件（继承父母）
        world.add_component(entity, SpeciationTrackerComponent(
            species_id=parent_species,
            original_species=parent_species,
            generation=parent_generation + 1,
            lineage_id=f"{parent_species}_{entity.id}",
        ))

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

        提示：
            若 variation > 1.0，某些基因值可能变为负数；
            具体负值的语义由使用该基因的系统决定。

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
    def _init_lifecycle(cls, preset: Dict[str, float]) -> LifeCycleComponent:
        """
        根据基因预设初始化动物生命周期

        动物生命周期阶段（复用植物阶段常量）：
            SEED        = 0  → 幼体期
            SPROUT      = 1  → 成长期
            VEGETATIVE  = 2  → 青年期
            MATURE      = 3  → 成年期（可繁殖）
            SENESCENCE  = 4  → 衰老期

        阶段时长由代谢速率和生长分配推导。
        """
        metabolism_rate = preset.get("metabolism_rate", 0.02)
        growth_partition = preset.get("growth_partition", 0.4)

        # 综合生长速率
        growth_rate = metabolism_rate * growth_partition
        scale = growth_rate * 100.0 + 0.5

        # 阶段时长（小时）：幼体 → 成长 → 青年 → 成年 → 衰老
        base_juvenile = 48.0 / scale
        base_growth = 168.0 / scale
        base_youth = 720.0 / scale
        base_mature = 4320.0 / scale
        base_senescence = 720.0 / scale

        stage_durations = [
            base_juvenile,
            base_growth,
            base_youth,
            base_mature,
            base_senescence,
        ]

        # GDD 需求（动物使用温度累积替代）
        optimal_temp = preset.get("optimal_temp", 37.0)
        gdd_juvenile = 10.0 * (25.0 / max(optimal_temp, 5.0))

        gdd_requirements = {
            0: gdd_juvenile,
            1: gdd_juvenile * 3.0,
            2: gdd_juvenile * 8.0,
            3: 0,  # 成熟期无 GDD 门槛
        }

        return LifeCycleComponent(
            stage=LifeCycleComponent.SEED,
            stage_durations=stage_durations,
            gdd_requirements=gdd_requirements,
            max_age=8760.0,  # 默认 1 年寿命
        )

    @classmethod
    def _attach_base_components(
        cls,
        world: World,
        entity: Entity,
        genome: GenomeComponent,
        lifecycle: LifeCycleComponent,
        preset: Dict[str, float],
        species: str,
        x: int,
        y: int,
    ) -> None:
        """
        为实体挂载动物生存必需的基础生物学组件

        挂载顺序：
            1. GenomeComponent      — 基因型（可遗传信息）
            2. PhenotypeComponent   — 表型容器（运行时特征计算结果）
            3. EnergyComponent      — 能量储备（max_energy=100.0）
            4. MorphologyComponent  — 形态外观
            5. LifeCycleComponent   — 生命周期（阶段推进与衰老管理）
            6. SpaceComponent       — 空间坐标
            7. AnimalComponent      — 动物标识与生态属性
            8. ImmuneComponent      — 免疫系统
            9. HealthStatusComponent — 健康状态

        Args:
            world: World 实例。
            entity: 目标实体。
            genome: 已构建好的基因组组件。
            lifecycle: 已初始化的生命周期组件。
            species: 物种标识名。
            x: 空间 X 坐标。
            y: 空间 Y 坐标。
        """
        from animal.components.animal_component import AnimalComponent

        # 基因型：决定个体的可遗传特征
        world.add_component(entity, genome)

        # 表型：运行时由基因表达系统填充
        world.add_component(entity, PhenotypeComponent())

        # 能量：基础最大能量池，value 默认从 0 开始，由外部系统初始化
        energy = EnergyComponent(max_energy=100.0)
        energy.value = 50.0  # 初始能量设为 50%，避免立即饿死
        world.add_component(entity, energy)

        # 形态：默认参数由 MorphologyComponent 的 dataclass 提供
        world.add_component(entity, MorphologyComponent())

        # 生命周期：管理从出生到死亡的各阶段推进
        world.add_component(entity, lifecycle)

        # 空间：固定在指定二维坐标，layer=0 表示地面层
        world.add_component(entity, SpaceComponent(x=x, y=y, layer=0))

        # 动物标识组件：食性由基因 preset 中的 diet_type 推导
        diet_type = preset.get("diet_type", 0.5)
        if diet_type > 0.7:
            diet = "carnivore"
        elif diet_type < 0.3:
            diet = "herbivore"
        else:
            diet = "omnivore"
        world.add_component(entity, AnimalComponent(species=species, diet=diet))

        # 食物链组件：标记营养级和生态角色（由 diet 推导）
        trophic_level = 3 if diet == "carnivore" else (2 if diet == "herbivore" else 2.5)
        niche = diet
        world.add_component(entity, FoodChainComponent(
            trophic_level=trophic_level,
            niche=niche,
        ))

        # 种群动态组件
        world.add_component(entity, PopulationComponent(
            growth_rate=preset.get("metabolism_rate", 0.02) * 2.0,
            carrying_capacity=50.0,
        ))

        # 分类组件：标记为动物
        subcategory = AnimalSubCategory.CARNIVORE if species == "predator" else AnimalSubCategory.HERBIVORE
        world.add_component(entity, CategoryComponent(
            category=EntityCategory.ANIMAL,
            subcategory=subcategory,
        ))

        # 扩展生物学组件：免疫、健康
        world.add_component(entity, ImmuneComponent())
        world.add_component(entity, HealthStatusComponent())

        # 新增动物生态组件
        from animal.components.animal_needs_component import AnimalNeedsComponent
        from animal.components.animal_social_component import AnimalSocialComponent
        from animal.components.animal_memory_component import AnimalMemoryComponent
        from animal.components.animal_territory_component import AnimalTerritoryComponent
        from animal.components.animal_reproduction_component import AnimalReproductionComponent
        from animal.components.animal_perception_component import AnimalPerceptionComponent
        from animal.components.animal_learning_component import AnimalLearningComponent

        world.add_component(entity, AnimalNeedsComponent())
        world.add_component(entity, AnimalSocialComponent())
        world.add_component(entity, AnimalMemoryComponent())
        world.add_component(entity, AnimalTerritoryComponent(
            center_x=float(x), center_y=float(y)
        ))
        world.add_component(entity, AnimalReproductionComponent())
        world.add_component(entity, AnimalPerceptionComponent())
        world.add_component(entity, AnimalLearningComponent())