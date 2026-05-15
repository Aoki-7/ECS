



from core.world import World
from core.system import System

from biology.components.phenotype_component import PhenotypeComponent
from biology.components.morphology_component import MorphologyComponent
from biology.components.energy_component import EnergyComponent

"""
| 基因                          | 结果   |
| --------------------------- | ---- |
| growth_rate ↑               | 植株更高 |
| leaf_size ↑                 | 叶片更大 |
| photosynthesis_efficiency ↑ | 颜色更深 |
| water_absorption ↑          | 根更深  |
"""

# Phenotype + Environment -> Energy
# Phenotype + Environment + Energy -> Morphology
# 基因+环境+能量->形态

class MorphologySystem(System):
    """
        根据基因、环境条件和能量更新形态。
    """
    def update(self, world: World, delta_hours: float = 1.0):

        for entity, (pheno, energy, morph) in \
            world.get_components(PhenotypeComponent, EnergyComponent, MorphologyComponent):
            
            pheno: PhenotypeComponent
            energy: EnergyComponent
            morph: MorphologyComponent

            growth_energy = energy.growth_pool

            if growth_energy <= 0:
                morph.wilting = min(1.0, morph.wilting + 0.01)
                continue

            # ===== 分配策略 =====
            leaf_bias = pheno.get("leaf_bias", 1.0)
            root_bias = pheno.get("root_bias", 1.0)
            stem_bias = pheno.get("stem_bias", 1.0)

            total = leaf_bias + root_bias + stem_bias

            leaf_e = growth_energy * leaf_bias / total
            root_e = growth_energy * root_bias / total
            stem_e = growth_energy * stem_bias / total

            # ===== 累积增长 =====
            morph.leaf_size += leaf_e * 0.01
            morph.root_depth += root_e * 0.01
            morph.height += stem_e * 0.01

            morph.leaf_count = int(morph.height * 2)

            # 消耗生长池
            energy.growth_pool = 0.0