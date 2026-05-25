# biology/factories/plant_factory.py

import random
from typing import Dict, Optional

from core.entity import Entity
from core.world import World

from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.components.energy_component import EnergyComponent
from biology.components.morphology_component import MorphologyComponent
from biology.genetics.gene import Gene



class PlantFactory:
    """
    通用植物工厂

    负责：
    - 创建 Entity
    - 构建 Genome
    - 自动挂载基础组件
    - 注册进 World
    """

    SPECIES_PRESETS: Dict[str, Dict[str, float]] = {

        "basic": {
            "max_photosynthesis_rate": 20.0, # 最大光合速率
            "light_use_efficiency": 0.05, # 光合利用效率
            "optimal_temp": 25.0, # 最佳温度
            "growth_partition": 0.6, # 生长分配比例
            "metabolism_rate": 0.01 # 代谢速率
        },
    }

    # -------------------------------------------------
    # 主入口：创建植物实体
    # -------------------------------------------------

    @staticmethod
    def create_plant(
        world: World,
        species: str = "basic",
        variation: float = 0.1,
        seed: Optional[int] = None
    ) -> Entity:
        """
        创建完整植物 Entity，并自动注册到 world
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

        if species not in PlantFactory.SPECIES_PRESETS:
            raise ValueError(f"Unknown species: {species}")

        if variation < 0:
            raise ValueError("variation must be >= 0")

        preset = PlantFactory.SPECIES_PRESETS[species]

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

        initial_energy = EnergyComponent()
        initial_energy.value = 10

        # 3️⃣ 挂载必须组件
        world.add_component(entity, genome)
        world.add_component(entity, PhenotypeComponent())
        world.add_component(entity, initial_energy)
        world.add_component(entity, MorphologyComponent())

        return entity