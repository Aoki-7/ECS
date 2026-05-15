


# biology/systems/mutation_system.py

import random

from core.world import World

from biology.components.genome_component import GenomeComponent


class MutationSystem:
    """
        变异系统，根据基因突变率对基因进行随机变异
        所有包含基因组的实体都会受到此系统的影响
    """
<<<<<<< HEAD
    def update(self, world: World, dt: float = 1.0):
=======
    def update(self, world: World):
>>>>>>> 65a14767a91c763628f1030bcdd9bce57d718edc
        for entity, [genome] in world.get_components(GenomeComponent):
            genome: GenomeComponent

            for gene in genome.genes:
                if random.random() < gene.mutation_rate:
                    gene.strength *= random.uniform(0.9, 1.1)