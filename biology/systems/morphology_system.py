#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/morphology_system.py
@说明:形态更新系统

根据生长池能量与基因分配策略，更新植物实体的形态参数：
    - 叶片大小、数量
    - 根系深度
    - 高度（受 max_height 上限约束）
    - 茎干粗细
    - 枯萎状态

读取的表型性状：
    leaf_bias, root_bias, stem_bias, max_height, stem_thickness_factor
"""

from core.world import World
from core.system import System

from biology.components.phenotype_component import PhenotypeComponent
from biology.components.morphology_component import MorphologyComponent
from biology.components.energy_component import EnergyComponent


class MorphologySystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    形态更新系统

    职责：
        - 读取 phenotype 中的器官分配偏向基因
        - 按 growth_pool 中的能量分配至叶、根、茎
        - 更新 MorphologyComponent 的各项参数
        - 处理能量耗尽时的枯萎逻辑
    """

    def update(self, world: World, delta_hours: float = 1.0) -> None:
        """
        执行形态更新

        Args:
            world: World 实例
            delta_hours: 时间步长（当前模型与时间无关，预留参数）
        """
        for entity, (pheno, energy, morph) in \
            world.get_components(
                PhenotypeComponent, EnergyComponent, MorphologyComponent
            ):

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
