#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物食草系统（重构版）

处理食草动物 (diet="herbivore") 的植物觅食行为：
    1. 优先访问记忆中的食物位置（记忆驱动觅食）
    2. 在 grazing_range 内搜索可食用植物
    3. 消耗植物的 harvestable_yield / ResourceComponent.amount
    4. 将消耗量转化为动物 EnergyComponent.value
    5. 觅食成功后记录食物位置到记忆

性能优化：
    - 批量查询附近实体，减少 query_entity 调用次数
    - 记忆缓存优先，避免重复空间搜索
"""

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from animal.components.animal_memory_component import AnimalMemoryComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem
from plant.components.plant_component import PlantComponent
from resource.components.resource_component import ResourceComponent
from identity.category_component import CategoryComponent
from identity.category import EntityCategory
from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent

import logging

logger = logging.getLogger(__name__)


class GrazingSystem(System):
    tick_interval = 10

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行食草更新"""
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        # 批量获取所有植物实体，建立快速查找缓存
        plant_cache = self._build_plant_cache(world)

        for entity, (animal, energy, space) in world.get_components(
            AnimalComponent, EnergyComponent, SpaceComponent
        ):
            if animal.diet not in ("herbivore", "omnivore"):
                continue

            if not self._is_hungry(energy):
                continue

            pheno = world.get_component(entity, PhenotypeComponent)
            if pheno is None:
                pheno = PhenotypeComponent()  # 使用默认表型
            morph = world.get_component(entity, MorphologyComponent)
            if morph is None:
                morph = MorphologyComponent()  # 使用默认形态
            max_graze, efficiency = self._derive_grazing_params(pheno, morph)

            # 记忆驱动：优先尝试记忆中的食物位置
            memory = world.get_component(entity, AnimalMemoryComponent)
            best_plant = self._find_plant_with_memory(
                world, space_system, entity, space, animal, memory, plant_cache
            )

            if best_plant is None:
                # 回退到空间搜索
                best_plant = self._find_best_plant_fast(
                    space_system, entity, space, animal, plant_cache
                )

            if best_plant is None:
                continue

            self._perform_graze(
                world, entity, energy, best_plant, max_graze, efficiency
            )

            # 记录成功觅食位置到记忆
            if memory:
                plant_entity = world.query_entity(best_plant)
                if plant_entity:
                    plant_comp = world.get_component(plant_entity, PlantComponent)
                    yield_val = plant_comp.harvestable_yield if plant_comp else 0.5
                    memory.add_memory(
                        space.x, space.y, "food",
                        entity_id=best_plant, value=yield_val
                    )

    def _build_plant_cache(self, world: World) -> dict[int, tuple]:
        """
        批量构建植物缓存：{entity_id -> (PlantComponent, ResourceComponent, CategoryComponent)}
        避免在循环中重复调用 get_component
        """
        cache = {}
        for entity, (plant, resource, cat) in world.get_components(
            PlantComponent, ResourceComponent, CategoryComponent
        ):
            if cat.category == EntityCategory.PLANT:
                cache[entity.id] = (plant, resource, cat)
        return cache

    def _is_hungry(self, energy: EnergyComponent) -> bool:
        """检查动物是否饥饿"""
        threshold = getattr(energy, "max_energy", 100.0) * 0.7
        return energy.value < threshold

    def _derive_grazing_params(self, pheno, morph):
        """根据表型和形态动态推导食草参数"""
        weight = morph.weight if morph else 10.0
        max_graze_amount = weight * 0.1
        metabolism = pheno.get("metabolism_rate", 0.02) if pheno else 0.02
        conversion_efficiency = max(1.0, 5.0 - metabolism * 80)
        return max_graze_amount, conversion_efficiency

    def _find_plant_with_memory(
        self, world: World, space_system: SpaceSystem,
        entity, space: SpaceComponent, animal: AnimalComponent,
        memory: AnimalMemoryComponent | None, plant_cache: dict
    ) -> int | None:
        """
        使用记忆优先查找食物。
        若记忆中有强食物记忆且位置附近确实有植物，直接返回。
        """
        if memory is None:
            return None

        food_mem = memory.recall_nearest(space.x, space.y, "food")
        if food_mem is None or food_mem.strength < 0.3:
            return None

        # 检查记忆中的位置附近是否有可食用植物
        nearby = space_system.query_radius(
            x=food_mem.x, y=food_mem.y, r=animal.grazing_range
        )

        best_plant = None
        best_yield = 0.0

        for candidate_id in nearby:
            if candidate_id == entity.id:
                continue
            if candidate_id not in plant_cache:
                continue

            plant_comp, _, _ = plant_cache[candidate_id]
            if plant_comp.harvestable_yield <= 0.1:
                continue
            if plant_comp.harvestable_yield > best_yield:
                best_yield = plant_comp.harvestable_yield
                best_plant = candidate_id

        return best_plant

    def _find_best_plant_fast(
        self, space_system: SpaceSystem, entity,
        space: SpaceComponent, animal: AnimalComponent,
        plant_cache: dict
    ) -> int | None:
        """
        使用空间索引搜索附近最佳可食用植物（优化版）。
        利用 plant_cache 避免重复 get_component 调用。
        """
        nearby = space_system.query_radius(
            x=space.x, y=space.y, r=animal.grazing_range
        )

        best_plant = None
        best_yield = 0.0

        for candidate_id in nearby:
            if candidate_id == entity.id:
                continue
            if candidate_id not in plant_cache:
                continue

            plant_comp, _, _ = plant_cache[candidate_id]
            if plant_comp.harvestable_yield <= 0.1:
                continue
            if plant_comp.harvestable_yield > best_yield:
                best_yield = plant_comp.harvestable_yield
                best_plant = candidate_id

        return best_plant

    def _perform_graze(
        self, world: World, entity, energy: EnergyComponent,
        best_plant_id: int, max_graze_amount: float, conversion_efficiency: float
    ) -> None:
        """执行啃食逻辑：消耗植物并增加动物能量"""
        best_plant_entity = world.query_entity(best_plant_id)
        if best_plant_entity is None:
            return

        plant_comp = world.get_component(best_plant_entity, PlantComponent)
        resource = world.get_component(best_plant_entity, ResourceComponent)

        best_yield = plant_comp.harvestable_yield if plant_comp else 0.0
        graze_amount = min(max_graze_amount, best_yield)

        if plant_comp is not None:
            plant_comp.harvestable_yield = max(0.0, plant_comp.harvestable_yield - graze_amount)
        if resource is not None:
            resource.amount = max(0.0, resource.amount - graze_amount)

        energy_gain = graze_amount * conversion_efficiency
        energy.value = min(
            getattr(energy, "max_energy", 1000.0),
            energy.value + energy_gain
        )

        # 更新需求组件
        needs = world.get_component(entity, AnimalNeedsComponent)
        if needs:
            needs.hunger = max(0.0, needs.hunger - graze_amount * 0.1)
            needs.last_satisfied = getattr(world, 'time', 0)

        logger.debug(
            f"[Grazing] E{entity.id} 啃食植物 E{best_plant_id}, "
            f"获得能量 {energy_gain:.1f} "
            f"(食量 {graze_amount:.2f}, 转化率 {conversion_efficiency:.2f})"
        )
