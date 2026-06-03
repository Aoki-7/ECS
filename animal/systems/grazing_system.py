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

import logging

logger = logging.getLogger(__name__)


class GrazingSystem(System):
    tick_interval = 10
    """
    食草系统

    职责：
        1. 遍历食草动物
        2. 使用空间索引查找附近植物
        3. 计算食量并消耗植物资源
        4. 将能量转移给动物
    """

    # 单次最大食量
    MAX_GRAZE_AMOUNT = 3.0

    def update(self, world: World, dt: float = 1.0) -> None:
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (animal, energy, space) in world.get_components(
            AnimalComponent, EnergyComponent, SpaceComponent
        ):
            if animal.diet not in ("herbivore", "omnivore"):
                continue

            # 只在饥饿时觅食（能量低于 70% 最大值）
            hunger_threshold = getattr(energy, "max_energy", 100.0) * 0.7
            if energy.value >= hunger_threshold:
                continue

            # 使用空间索引搜索附近植物
            nearby = space_system.query_radius(
                x=space.x, y=space.y, r=animal.grazing_range
            )

            best_plant = None
            best_yield = 0.0

            for candidate_id in nearby:
                if candidate_id == entity.id:
                    continue

                plant_comp = world.get_component_by_id(candidate_id, PlantComponent)
                if plant_comp is None:
                    continue

                # 只食用有可收获量的植物
                if plant_comp.harvestable_yield <= 0.1:
                    continue

                # 优先选择产量最高的
                if plant_comp.harvestable_yield > best_yield:
                    best_yield = plant_comp.harvestable_yield
                    best_plant = candidate_id

            if best_plant is None:
                continue

            # 计算实际食量
            graze_amount = min(self.MAX_GRAZE_AMOUNT, best_yield)

            # 消耗植物
            plant_comp = world.get_component_by_id(best_plant, PlantComponent)
            resource = world.get_component_by_id(best_plant, ResourceComponent)

            if plant_comp is not None:
                plant_comp.harvestable_yield -= graze_amount
                if plant_comp.harvestable_yield < 0:
                    plant_comp.harvestable_yield = 0.0

            if resource is not None:
                resource.amount -= graze_amount
                if resource.amount < 0:
                    resource.amount = 0.0

            # 增加动物能量（营养转化率约 30%）
            energy_gain = graze_amount * 3.0
            energy.value = min(
                getattr(energy, "max_energy", 1000.0),
                energy.value + energy_gain
            )

            logger.debug(
                f"[Grazing] E{entity.id} 啃食植物 E{best_plant}, "
                f"获得能量 {energy_gain:.1f}"
            )
