#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/morphology_system.py
@说明:形态更新系统 v2.0 — 外观由生长过程动态决定

设计原则：
    1. 不读取任何硬编码外观参数（leaf_bias, root_bias, stem_bias, max_height 等）
    2. 基因只提供生理潜力参数（metabolism_rate, growth_partition, maintenance_cost, storage_partition）
    3. 外观（高度、茎粗、叶数）由生长过程动态推导：
       - 生物量累积 → 高度（异速生长 allometry）
       - 生物量 → 茎粗（经典 3/8 幂律）
       - 叶面积 → 叶片数量
    4. 无硬编码高度上限——植物大小由能量供给和维护成本自然限制

读取的表型性状：
    metabolism_rate, growth_partition, maintenance_cost, storage_partition
"""

import math

from core.world import World
from core.system import System

from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from resource.components.resource_component import ResourceComponent
from plant.components.canopy_component import CanopyComponent


class MorphologySystem(System):
    tick_interval = 20
    """
    形态更新系统

    职责：
        1. 读取纯生理基因参数
        2. 按 growth_pool 能量驱动生物量累积
        3. 通过异速生长(allometry)从生物量推导外观
        4. 维护消耗随体型超线性增长，自然限制最大尺寸
    """

    def update(self, world: World, delta_hours: float = 1.0) -> None:
        """
        执行形态更新

        Args:
            world: World 实例
            delta_hours: 时间步长（预留）
        """
        for entity, (pheno, energy, morph) in world.get_components(
            PhenotypeComponent, EnergyComponent, MorphologyComponent
        ):
            growth_energy = energy.growth_pool

            # ——— 能量耗尽 → 枯萎 ———
            if growth_energy <= 0:
                morph.wilting = min(1.0, morph.wilting + 0.01)
                continue

            # ——— 读取纯生理基因 ———
            metabolism_rate = pheno.get("metabolism_rate", 0.01)
            growth_partition = pheno.get("growth_partition", 0.6)
            maintenance_cost = pheno.get("maintenance_cost", 0.02)
            storage_partition = pheno.get("storage_partition", 0.2)

            # ——— 可用于形态生长的能量 ———
            effective_growth = growth_energy * growth_partition

            # ——— 生物量累积 ———
            # 生长能量的 10% 转化为生物量（受代谢速率调节）
            biomass_increment = effective_growth * metabolism_rate * 10.0
            morph.weight += biomass_increment

            # ——— 高度（异速生长: 高度 ∝ 生物量^(2/3)） ———
            # 没有 max_height 硬上限！
            # 系数 5.0 使草本(weight≈20)高度约 30cm，乔木(weight≈300)高度约 150cm
            height_target = 5.0 * (morph.weight ** (2.0 / 3.0))
            # 渐进逼近，避免突变
            morph.height += (height_target - morph.height) * 0.15

            # ——— 根系深度（与高度成比例，0.3~0.6 倍） ———
            root_target = morph.height * (0.3 + 0.3 * storage_partition)
            morph.root_depth += (root_target - morph.root_depth) * 0.1

            # ——— 茎粗（经典异速生长: 茎粗 ∝ 生物量^(3/8)） ———
            # 不用硬编码 stem_thickness_factor
            thickness_target = 0.1 + 0.05 * (morph.weight ** (3.0 / 8.0))
            morph.stem_thickness += (thickness_target - morph.stem_thickness) * 0.1

            # ——— 叶片大小（与生物量成正比） ———
            leaf_size_target = 0.1 + 0.02 * morph.weight
            morph.leaf_size += (leaf_size_target - morph.leaf_size) * 0.1

            # ——— 叶片数量（由叶面积指数决定） ———
            canopy = world.get_component(entity, CanopyComponent)
            if canopy is not None:
                # 更新冠层 LAI
                canopy.leaf_area_index = min(
                    8.0, morph.leaf_size * 0.5 + morph.weight * 0.02
                )
                morph.leaf_count = max(1, int(canopy.leaf_area_index * 6))
            else:
                morph.leaf_count = max(1, int(morph.leaf_size * 3))

            # ——— 恢复枯萎状态 ———
            if morph.wilting > 0:
                morph.wilting = max(0.0, morph.wilting - 0.02)

            # ——— 维护消耗（随体型超线性增长，自然限制最大尺寸） ———
            # effective_maintenance = weight * maintenance_cost * (1 + weight * 0.001)
            # 大树维护成本极高，能量不足时自然停止生长
            base_maintenance = morph.weight * maintenance_cost
            size_penalty = 1.0 + morph.weight * 0.001  # 超线性惩罚
            total_maintenance = base_maintenance * size_penalty
            energy.value -= total_maintenance

            # ——— 储存积累 ———
            # 部分能量进入储存池（影响后续抗逆、休眠等）
            storage_gain = effective_growth * storage_partition * 0.05
            # 暂存到 energy.value（简化模型）
            energy.value += storage_gain

            # ——— 同步资源组件的可收获量 ———
            resource = world.get_component(entity, ResourceComponent)
            if resource is not None:
                resource.amount = morph.weight * 0.5

            # ——— 消耗生长池 ———
            energy.growth_pool = 0.0
