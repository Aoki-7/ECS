# biology/factories/plant_factory.py

import random
from typing import Dict, Optional

from core.entity import Entity
from core.world import World

from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.components.energy_component import EnergyComponent
from biology.components.morphology_component import MorphologyComponent
from biology.components.life_cycle_component import LifeCycleComponent
from biology.genetics.gene import Gene

from space.space_component import SpaceComponent


class PlantFactory:
    """
    通用植物工厂

    负责：
    - 创建 Entity
    - 构建 Genome（13 个维度基因）
    - 自动挂载基础组件
    - 注册进 World

    基因维度（按功能分类）：
    ─ 光合系统：max_photosynthesis_rate, light_use_efficiency, shade_tolerance
    ─ 温度响应：optimal_temp, cold_tolerance, heat_tolerance
    ─ 水分利用：water_use_efficiency
    ─ 代谢分配：metabolism_rate, growth_partition
    ─ 形态分配：leaf_bias, root_bias, stem_bias, max_height, stem_thickness_factor
    ─ 繁殖策略：seed_production, dispersal_radius
    """

    # ==========================================================
    # 物种基因预设（13 个核心基因）
    # ==========================================================

    SPECIES_PRESETS: Dict[str, Dict[str, float]] = {

        # ---- 🌿 基础草本 ----
        "basic": {
            # 光合
            "max_photosynthesis_rate": 20.0,
            "light_use_efficiency": 0.05,
            "shade_tolerance": 0.3,
            # 温度
            "optimal_temp": 25.0,
            "cold_tolerance": 0.4,
            "heat_tolerance": 0.5,
            # 水分
            "water_use_efficiency": 0.05,
            # 代谢
            "metabolism_rate": 0.01,
            "growth_partition": 0.6,
            # 形态分配
            "leaf_bias": 1.0,
            "root_bias": 1.0,
            "stem_bias": 1.0,
            "max_height": 60.0,
            "stem_thickness_factor": 0.15,
            # 繁殖
            "seed_production": 1.0,
            "dispersal_radius": 3.0,
        },

        # ---- ⚡ 速生杂草 ----
        "fast": {
            "max_photosynthesis_rate": 35.0,
            "light_use_efficiency": 0.09,
            "shade_tolerance": 0.2,
            "optimal_temp": 28.0,
            "cold_tolerance": 0.2,
            "heat_tolerance": 0.6,
            "water_use_efficiency": 0.06,
            "metabolism_rate": 0.02,
            "growth_partition": 0.7,
            "leaf_bias": 2.0,
            "root_bias": 0.5,
            "stem_bias": 1.0,
            "max_height": 40.0,
            "stem_thickness_factor": 0.08,
            "seed_production": 2.0,
            "dispersal_radius": 5.0,
        },

        # ---- 🌲 乔木 ----
        "tree": {
            "max_photosynthesis_rate": 15.0,
            "light_use_efficiency": 0.04,
            "shade_tolerance": 0.5,
            "optimal_temp": 22.0,
            "cold_tolerance": 0.6,
            "heat_tolerance": 0.4,
            "water_use_efficiency": 0.06,
            "metabolism_rate": 0.005,
            "growth_partition": 0.5,
            "leaf_bias": 1.5,
            "root_bias": 1.5,
            "stem_bias": 3.0,
            "max_height": 300.0,
            "stem_thickness_factor": 0.5,
            "seed_production": 0.5,
            "dispersal_radius": 10.0,
        },

        # ---- ❄️ 耐寒型 ----
        "cold_resistant": {
            "max_photosynthesis_rate": 18.0,
            "light_use_efficiency": 0.06,
            "shade_tolerance": 0.4,
            "optimal_temp": 15.0,
            "cold_tolerance": 0.9,
            "heat_tolerance": 0.2,
            "water_use_efficiency": 0.05,
            "metabolism_rate": 0.008,
            "growth_partition": 0.5,
            "leaf_bias": 0.8,
            "root_bias": 1.5,
            "stem_bias": 0.5,
            "max_height": 40.0,
            "stem_thickness_factor": 0.12,
            "seed_production": 0.8,
            "dispersal_radius": 4.0,
        },

        # ---- 🏜️ 耐旱型 ----
        "drought_resistant": {
            "max_photosynthesis_rate": 10.0,
            "light_use_efficiency": 0.03,
            "shade_tolerance": 0.2,
            "optimal_temp": 30.0,
            "cold_tolerance": 0.1,
            "heat_tolerance": 0.8,
            "water_use_efficiency": 0.10,
            "metabolism_rate": 0.005,
            "growth_partition": 0.4,
            "leaf_bias": 0.3,
            "root_bias": 3.0,
            "stem_bias": 0.5,
            "max_height": 20.0,
            "stem_thickness_factor": 0.3,
            "seed_production": 0.5,
            "dispersal_radius": 6.0,
        },

        # ---- 🌑 耐阴型 ----
        "shade_tolerant": {
            "max_photosynthesis_rate": 8.0,
            "light_use_efficiency": 0.12,
            "shade_tolerance": 0.9,
            "optimal_temp": 22.0,
            "cold_tolerance": 0.5,
            "heat_tolerance": 0.3,
            "water_use_efficiency": 0.07,
            "metabolism_rate": 0.008,
            "growth_partition": 0.5,
            "leaf_bias": 2.5,
            "root_bias": 0.8,
            "stem_bias": 0.5,
            "max_height": 30.0,
            "stem_thickness_factor": 0.1,
            "seed_production": 0.6,
            "dispersal_radius": 2.0,
        },

        # ---- 💧 水生型 ----
        "aquatic": {
            "max_photosynthesis_rate": 25.0,
            "light_use_efficiency": 0.07,
            "shade_tolerance": 0.4,
            "optimal_temp": 28.0,
            "cold_tolerance": 0.3,
            "heat_tolerance": 0.6,
            "water_use_efficiency": 0.03,
            "metabolism_rate": 0.015,
            "growth_partition": 0.6,
            "leaf_bias": 2.0,
            "root_bias": 0.3,
            "stem_bias": 1.5,
            "max_height": 80.0,
            "stem_thickness_factor": 0.08,
            "seed_production": 1.5,
            "dispersal_radius": 8.0,
        },

        # ---- 🌵 多肉型 ----
        "succulent": {
            "max_photosynthesis_rate": 6.0,
            "light_use_efficiency": 0.02,
            "shade_tolerance": 0.2,
            "optimal_temp": 32.0,
            "cold_tolerance": 0.2,
            "heat_tolerance": 0.9,
            "water_use_efficiency": 0.15,
            "metabolism_rate": 0.003,
            "growth_partition": 0.3,
            "leaf_bias": 1.5,
            "root_bias": 1.0,
            "stem_bias": 0.5,
            "max_height": 15.0,
            "stem_thickness_factor": 0.6,
            "seed_production": 0.3,
            "dispersal_radius": 2.0,
        },

        # ---- 🌿 藤本型 ----
        "vine": {
            "max_photosynthesis_rate": 22.0,
            "light_use_efficiency": 0.06,
            "shade_tolerance": 0.5,
            "optimal_temp": 26.0,
            "cold_tolerance": 0.3,
            "heat_tolerance": 0.6,
            "water_use_efficiency": 0.05,
            "metabolism_rate": 0.015,
            "growth_partition": 0.7,
            "leaf_bias": 2.5,
            "root_bias": 0.5,
            "stem_bias": 2.0,
            "max_height": 120.0,
            "stem_thickness_factor": 0.06,
            "seed_production": 1.2,
            "dispersal_radius": 6.0,
        },
    }

    # ==========================================================
    # 物种生命周期预设
    # ==========================================================

    SPECIES_LIFECYCLE: Dict[str, Dict] = {
        "basic": {
            "max_age": 8760,                      # ~1年
            "stage_durations": [48, 168, 720, 4320, 720],
            "gdd_requirements": {0: 10, 1: 30, 2: 80, 3: 0},
        },
        "fast": {
            "max_age": 4320,                      # ~6个月
            "stage_durations": [24, 72, 360, 2160, 360],
            "gdd_requirements": {0: 5, 1: 15, 2: 40, 3: 0},
        },
        "tree": {
            "max_age": 175200,                    # ~20年
            "stage_durations": [720, 2160, 43200, 86400, 8640],
            "gdd_requirements": {0: 20, 1: 50, 2: 200, 3: 0},
        },
        "cold_resistant": {
            "max_age": 13140,                     # ~1.5年
            "stage_durations": [72, 240, 1080, 6480, 1080],
            "gdd_requirements": {0: 8, 1: 20, 2: 60, 3: 0},
        },
        "drought_resistant": {
            "max_age": 26280,                     # ~3年
            "stage_durations": [120, 360, 2160, 12960, 1440],
            "gdd_requirements": {0: 15, 1: 40, 2: 120, 3: 0},
        },
        "shade_tolerant": {
            "max_age": 17520,                     # ~2年
            "stage_durations": [96, 336, 1440, 8640, 1440],
            "gdd_requirements": {0: 8, 1: 25, 2: 60, 3: 0},
        },
        "aquatic": {
            "max_age": 8760,                      # ~1年
            "stage_durations": [48, 120, 480, 4320, 720],
            "gdd_requirements": {0: 12, 1: 35, 2: 90, 3: 0},
        },
        "succulent": {
            "max_age": 26280,                     # ~3年
            "stage_durations": [168, 720, 4320, 12960, 2880],
            "gdd_requirements": {0: 20, 1: 50, 2: 150, 3: 0},
        },
        "vine": {
            "max_age": 13140,                     # ~1.5年
            "stage_durations": [72, 240, 1080, 6480, 1080],
            "gdd_requirements": {0: 10, 1: 30, 2: 80, 3: 0},
        },
    }

    # ==========================================================
    # 主入口
    # ==========================================================

    @staticmethod
    def create_plant(
        world: World,
        species: str = "basic",
        variation: float = 0.1,
        seed: Optional[int] = None,
        x: int = 0,
        y: int = 0,
    ) -> Entity:
        """
        创建完整植物 Entity

        参数：
            world: World
            species: str          # 物种名（共 9 种）
            variation: float      # 变异系数 (0~1)
            seed: Optional[int]   # 随机种子
            x, y: int             # 空间坐标

        返回：
            Entity（含 16 个基因 + 6 个组件）
        """
        if seed is not None:
            random.seed(seed)

        if species not in PlantFactory.SPECIES_PRESETS:
            raise ValueError(f"Unknown species: {species}. "
                             f"Available: {list(PlantFactory.SPECIES_PRESETS.keys())}")

        if variation < 0:
            raise ValueError("variation must be >= 0")

        preset = PlantFactory.SPECIES_PRESETS[species]

        # 1) 创建实体
        entity = world.create_entity()

        # 2) 构建 Genome（所有基因带变异）
        genome = GenomeComponent()
        for trait_name, base_value in preset.items():
            delta = base_value * variation
            actual_value = random.uniform(
                base_value - delta,
                base_value + delta
            )
            genome.add_gene(Gene(
                name=f"{species.upper()}_{trait_name.upper()}",
                expression_target=trait_name,
                strength=actual_value
            ))

        # 3) 初始化组件
        initial_energy = EnergyComponent()
        initial_energy.value = 10.0

        lc_config = PlantFactory.SPECIES_LIFECYCLE.get(species, PlantFactory.SPECIES_LIFECYCLE["basic"])
        lifecycle = LifeCycleComponent(
            stage=LifeCycleComponent.SEED,
            max_age=lc_config["max_age"],
            stage_durations=lc_config["stage_durations"],
            gdd_requirements=lc_config["gdd_requirements"],
        )

        # 4) 挂载组件
        world.add_component(entity, genome)
        world.add_component(entity, PhenotypeComponent())
        world.add_component(entity, initial_energy)
        world.add_component(entity, MorphologyComponent())
        world.add_component(entity, lifecycle)
        world.add_component(entity, SpaceComponent(x=x, y=y, layer=0))

        return entity

    # ==========================================================
    # 子代繁殖工厂
    # ==========================================================

    @staticmethod
    def create_plant_from_genome(
        world: World,
        parent_genome: GenomeComponent,
        x: int = 0,
        y: int = 0,
        variation: float = 0.15,
    ) -> Entity:
        """
        基于亲本 Genome 创建子代（无性繁殖 + 变异）
        """
        entity = world.create_entity()

        child_genome = parent_genome.copy()
        child_genome.mutate(mutation_rate=variation)

        init_energy = EnergyComponent()
        init_energy.value = 5.0

        lifecycle = LifeCycleComponent(stage=LifeCycleComponent.SEED)

        world.add_component(entity, child_genome)
        world.add_component(entity, PhenotypeComponent())
        world.add_component(entity, init_energy)
        world.add_component(entity, MorphologyComponent())
        world.add_component(entity, lifecycle)
        world.add_component(entity, SpaceComponent(x=x, y=y, layer=0))

        return entity
