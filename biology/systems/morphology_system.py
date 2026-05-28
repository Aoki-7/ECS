# biology/systems/morphology_system.py
#
# 根据生长池能量 + 基因分配策略更新形态组件
#
# 读取的基因：
#   leaf_bias, root_bias, stem_bias  — 器官分配偏向
#   max_height                        — 高度上限
#   stem_thickness_factor             — 茎粗系数

from core.world import World
from core.system import System

from biology.components.phenotype_component import PhenotypeComponent
from biology.components.morphology_component import MorphologyComponent
from biology.components.energy_component import EnergyComponent


class MorphologySystem(System):
    """
    根据基因、环境条件和能量更新形态。
    """
    def update(self, world: World, delta_hours: float = 1.0):

        for entity, (pheno, energy, morph) in \
            world.get_components(PhenotypeComponent, EnergyComponent, MorphologyComponent):

            growth_energy = energy.growth_pool

            # ——— 能量耗尽 → 枯萎 ———
            if growth_energy <= 0:
                morph.wilting = min(1.0, morph.wilting + 0.01)
                continue

            # ——— 读取基因分配偏向 ———
            leaf_bias = pheno.get("leaf_bias", 1.0)
            root_bias = pheno.get("root_bias", 1.0)
            stem_bias = pheno.get("stem_bias", 1.0)
            max_height = pheno.get("max_height", 60.0)
            stem_thickness_factor = pheno.get("stem_thickness_factor", 0.15)

            total = leaf_bias + root_bias + stem_bias

            leaf_e = growth_energy * leaf_bias / total
            root_e = growth_energy * root_bias / total
            stem_e = growth_energy * stem_bias / total

            # ——— 高度上限约束 ———
            height_before = morph.height

            # 生长分配
            morph.leaf_size += leaf_e * 0.01
            morph.root_depth += root_e * 0.01
            morph.height += stem_e * 0.01

            # 高度硬上限
            if morph.height > max_height:
                morph.height = max_height

            # ——— 茎粗（随高度增长而增粗） ———
            # 实际茎粗 = 基础值 + 高度 * 厚度因子
            morph.stem_thickness = stem_thickness_factor * (morph.height / 10.0)

            # ——— 叶片数量（与高度相关） ———
            morph.leaf_count = int(morph.height * 2)

            # ——— 恢复枯萎状态 ———
            if morph.wilting > 0:
                morph.wilting = max(0.0, morph.wilting - 0.02)

            # ——— 消耗生长池 ———
            energy.growth_pool = 0.0
