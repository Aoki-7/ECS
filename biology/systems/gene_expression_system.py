



# biology/systems/gene_expression_system.py



from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.traits.trait import Trait

from core.world import World

class GeneExpressionSystem:
    """
    基因表达系统
    根据基因组信息计算表型特征
        目前实现简单的线性表达模型
    """
    def update(self, world: World, dt: float = 1.0):
    def update(self, world: World):

        for _, [genome, phenotype] in world.get_components(GenomeComponent, PhenotypeComponent):

            genome: GenomeComponent
            phenotype: PhenotypeComponent

            # 1 清理旧 gene trait
            phenotype.remove_by_source("gene")

            # 2 累积表达值
            accumulator: dict[str, float] = {}

            for gene in genome.genes:
                target = gene.expression_target
                accumulator.setdefault(target, 0.0)
                accumulator[target] += gene.express()
            # 3 写入 phenotype
            for trait_name, value in accumulator.items():
                trait = Trait(
                    name=trait_name,
                    value=value,
                    source="gene"
                )

                # trait约束逻辑在System层
                trait.clamp()

                phenotype.set_trait(trait)