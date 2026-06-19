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
        """执行形态更新"""
        for entity, (pheno, energy, morph) in world.get_components(
            PhenotypeComponent, EnergyComponent, MorphologyComponent
        ):
            self._update_morphology_for_entity(world, entity, pheno, energy, morph)

    def _update_morphology_for_entity(self, world, entity, pheno, energy, morph):
        """单个实体的形态更新逻辑"""
        growth_energy = energy.growth_pool

        if growth_energy <= 0:
            morph.wilting = min(1.0, morph.wilting + 0.01)
            return

        metabolism_rate = PhenotypeSystem.get(pheno, "metabolism_rate", 0.01)
        growth_partition = PhenotypeSystem.get(pheno, "growth_partition", 0.6)
        maintenance_cost = PhenotypeSystem.get(pheno, "maintenance_cost", 0.02)
        storage_partition = PhenotypeSystem.get(pheno, "storage_partition", 0.2)

        effective_growth = growth_energy * growth_partition
        self._update_biomass_and_structure(morph, effective_growth, metabolism_rate, storage_partition)
        self._update_canopy(world, entity, morph)
        self._apply_maintenance_and_storage(world, entity, energy, morph, effective_growth, maintenance_cost, storage_partition)

        if morph.wilting > 0:
            morph.wilting = max(0.0, morph.wilting - 0.02)

        energy.growth_pool = 0.0

    def _update_biomass_and_structure(self, morph, effective_growth, metabolism_rate, storage_partition):
        """更新生物量和结构形态"""
        biomass_increment = effective_growth * metabolism_rate * 10.0
        morph.weight += biomass_increment

        height_target = 5.0 * (morph.weight ** (2.0 / 3.0))
        morph.height += (height_target - morph.height) * 0.15

        root_target = morph.height * (0.3 + 0.3 * storage_partition)
        morph.root_depth += (root_target - morph.root_depth) * 0.1

        thickness_target = 0.1 + 0.05 * (morph.weight ** (3.0 / 8.0))
        morph.stem_thickness += (thickness_target - morph.stem_thickness) * 0.1

        leaf_size_target = 0.1 + 0.02 * morph.weight
        morph.leaf_size += (leaf_size_target - morph.leaf_size) * 0.1

    def _update_canopy(self, world, entity, morph):
        """更新冠层和叶片数量"""
        canopy = world.get_component(entity, CanopyComponent)
        if canopy is not None:
            canopy.leaf_area_index = min(8.0, morph.leaf_size * 0.5 + morph.weight * 0.02)
            morph.leaf_count = max(1, int(canopy.leaf_area_index * 6))
        else:
            morph.leaf_count = max(1, int(morph.leaf_size * 3))

    def _apply_maintenance_and_storage(self, world, entity, energy, morph, effective_growth, maintenance_cost, storage_partition):
        """应用维护消耗、储存积累和资源同步"""
        base_maintenance = morph.weight * maintenance_cost
        size_penalty = 1.0 + morph.weight * 0.001
        energy.value -= base_maintenance * size_penalty

        storage_gain = effective_growth * storage_partition * 0.05
        energy.value += storage_gain

        resource = world.get_component(entity, ResourceComponent)
        if resource is not None:
            resource.amount = morph.weight * 0.5
