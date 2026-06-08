#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物食草系统

处理食草动物 (diet="herbivore") 的植物觅食行为：
    1. 在 grazing_range 内搜索可食用植物
    2. 消耗植物的 harvestable_yield / ResourceComponent.amount
    3. 将消耗量转化为动物 EnergyComponent.value

与 plant 模块的配合：
    读取 PlantComponent 和 ResourceComponent 判断可食用性，
    修改植物产量并可能触发植物死亡（过度啃食）。
"""

import math

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem
from plant.components.plant_component import PlantComponent
from resource.components.resource_component import ResourceComponent
from core.category_component import CategoryComponent
from core.category import EntityCategory
from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent

import logging

logger = logging.getLogger(__name__)


class GrazingSystem(System):
    tick_interval = 10
    """
    食草系统

    职责：
        1. 遍历食草动物
        2. 使用空间索引查找附近植物
        3. 计算食量并消耗植物资源（食量由动物体重基因决定）
        4. 将能量转移给动物（转化率由代谢率基因决定）
    """

    def update(self, world: World, dt: float = 1.0) -> None:
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (animal, energy, space) in world.get_components(
            AnimalComponent, EnergyComponent, SpaceComponent
        ):
            if animal.diet not in ("herbivore", "omnivore"):
                continue

            pheno = world.get_component(entity, PhenotypeComponent)
            morph = world.get_component(entity, MorphologyComponent)
            max_graze_amount, conversion_efficiency = self._derive_grazing_params(pheno, morph)

            hunger_threshold = getattr(energy, "max_energy", 100.0) * 0.7
            if energy.value >= hunger_threshold:
                continue

            best_plant = self._find_best_plant(world, space_system, entity, space, animal)
            if best_plant is None:
                continue

            self._perform_graze(world, entity, energy, best_plant, max_graze_amount, conversion_efficiency)

    def _derive_grazing_params(self, pheno, morph):
        """根据表型和形态动态推导食草参数"""
        weight = morph.weight if morph else 10.0
        max_graze_amount = weight * 0.1
        metabolism = pheno.get("metabolism_rate", 0.02) if pheno else 0.02
        conversion_efficiency = max(1.0, 5.0 - metabolism * 80)
        return max_graze_amount, conversion_efficiency

    def _find_best_plant(self, world, space_system, entity, space, animal):
        """使用空间索引搜索附近最佳可食用植物，返回 plant_id 或 None"""
        nearby = space_system.query_radius(x=space.x, y=space.y, r=animal.grazing_range)
        best_plant = None
        best_yield = 0.0

        for candidate_id in nearby:
            if candidate_id == entity.id:
                continue
            candidate = world.query_entity(candidate_id)
            plant_comp = world.get_component(candidate, PlantComponent) if candidate else None
            if plant_comp is None:
                continue

            cat = world.get_component(candidate, CategoryComponent)
            if cat is not None and cat.category != EntityCategory.PLANT:
                continue
            if plant_comp.harvestable_yield <= 0.1:
                continue
            if plant_comp.harvestable_yield > best_yield:
                best_yield = plant_comp.harvestable_yield
                best_plant = candidate_id

        return best_plant

    def _perform_graze(self, world, entity, energy, best_plant_id, max_graze_amount, conversion_efficiency):
        """执行啃食逻辑：消耗植物并增加动物能量"""
        best_plant_entity = world.query_entity(best_plant_id)
        plant_comp = world.get_component(best_plant_entity, PlantComponent) if best_plant_entity else None
        resource = world.get_component(best_plant_entity, ResourceComponent) if best_plant_entity else None

        best_yield = plant_comp.harvestable_yield if plant_comp else 0.0
        graze_amount = min(max_graze_amount, best_yield)

        if plant_comp is not None:
            plant_comp.harvestable_yield = max(0.0, plant_comp.harvestable_yield - graze_amount)
        if resource is not None:
            resource.amount = max(0.0, resource.amount - graze_amount)

        energy_gain = graze_amount * conversion_efficiency
        energy.value = min(getattr(energy, "max_energy", 1000.0), energy.value + energy_gain)

        logger.debug(
            f"[Grazing] E{entity.id} 啃食植物 E{best_plant_id}, "
            f"获得能量 {energy_gain:.1f} "
            f"(食量 {graze_amount:.2f}, 转化率 {conversion_efficiency:.2f})"
        )
