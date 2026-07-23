#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/gene_expression_system.py
@说明:基因表达系统

根据 GenomeComponent 中存储的基因信息，计算每个 trait 的表达值，
并将结果写入 PhenotypeComponent。

表达模型：
    1. 遍历所有 Gene，按 expression_target 分组累加 express() 值
    2. 清理旧来源为 "gene" 的 trait
    3. 将累加结果以 Trait(source="gene") 形式写入 phenotype

注意：
    该系统应在每帧早期执行，确保后续 GrowthSystem、MorphologySystem
    读取到的 phenotype 是最新的基因表达结果。
"""

from core.system import System
from core.world import World

from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.traits.trait import Trait
from biology.systems.phenotype_system import PhenotypeSystem


class GeneExpressionSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    基因表达系统

    职责：
        - 读取 GenomeComponent 中的所有 Gene
        - 按 expression_target 聚合表达值
        - 将聚合结果写入 PhenotypeComponent（来源标记为 "gene"）

    当前实现为简单的线性加和模型，后续可扩展 dominance 和环境调制。
    """

    def __init__(self):
        super().__init__()

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行基因表达

        Args:
            world: World 实例
            dt: 时间步长（当前表达模型与时间无关，预留参数）
        """
        for _, [genome, phenotype] in world.get_components(
            GenomeComponent, PhenotypeComponent
        ):
            genome: GenomeComponent
            phenotype: PhenotypeComponent

            # 1️⃣ 清理旧 gene trait，避免跨帧累加
            PhenotypeSystem.remove_by_source(phenotype, "gene")

            # 2️⃣ 按 expression_target 累加表达值
            accumulator: dict[str, float] = {}

            for gene in genome.genes:
                target = gene.expression_target
                accumulator.setdefault(target, 0.0)
                accumulator[target] += gene.express()

            # 3️⃣ 将累加结果写入 phenotype
            for trait_name, value in accumulator.items():
                trait = Trait(
                    name=trait_name,
                    value=value,
                    source="gene"
                )

                # trait 约束逻辑在 System 层统一处理
                trait.clamp()

                PhenotypeSystem.set_trait(phenotype, trait)