# biology/factories/animal_factory.py

import random
from typing import Dict, Optional

from core.entity import Entity
from core.world import World

from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.components.energy_component import EnergyComponent
from biology.components.morphology_component import MorphologyComponent
from biology.genetics.gene import Gene


class AnimalFactory:
    """
    通用动物工厂

    负责：
    - 创建 Entity
    - 构建 Genome
    - 自动挂载基础组件
    - 注册进 World
    """

    SPECIES_PRESETS: Dict[str, Dict[str, float]] = {
        "basic": {
            "max_hunger_rate": 5.0,  # 最大饥饿速率
            "metabolism_rate": 0.02,  # 代谢速率
            "optimal_temp": 37.0,  # 最佳体温
            "growth_partition": 0.4,  # 生长分配比例
            "speed_factor": 1.0,  # 移动速度系数
            "sensing_range": 5.0,  # 感知范围
        },
        "fast": {
            "max_hunger_rate": 8.0,
            "metabolism_rate": 0.04,
            "optimal_temp": 37.0,
            "growth_partition": 0.3,
            "speed_factor": 2.5,
            "sensing_range": 10.0,
        },
        "tank": {
            "max_hunger_rate": 3.0,
            "metabolism_rate": 0.01,
            "optimal_temp": 36.0,
            "growth_partition": 0.6,
            "speed_factor": 0.5,
            "sensing_range": 3.0,
        },
    }

    # -------------------------------------------------
    # 主入口：创建动物实体
    # -------------------------------------------------

    @staticmethod
    def create_animal(
        world: World,
        species: str = "basic",
        variation: float = 0.1,
        seed: Optional[int] = None
    ) -> Entity:
        """
        创建完整动物 Entity，并自动注册到 world

        参数：
            world: World # 世界
            species: str # 物种
            variation: float # 变异系数
            seed: Optional[int] # 随机数种子

        返回：
            Entity
        """

        if seed is not None:
            random.seed(seed)

        if species not in AnimalFactory.SPECIES_PRESETS:
            raise ValueError(f"Unknown species: {species}")

        if variation < 0:
            raise ValueError("variation must be >= 0")

        preset = AnimalFactory.SPECIES_PRESETS[species]

        # 1️⃣ 创建实体
        entity = world.create_entity()

        # 2️⃣ 构建 Genome
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

        # 3️⃣ 挂载必须组件
        world.add_component(entity, genome)
        world.add_component(entity, PhenotypeComponent())
        world.add_component(entity, EnergyComponent(max_energy=100.0))
        world.add_component(entity, MorphologyComponent())

        return entity