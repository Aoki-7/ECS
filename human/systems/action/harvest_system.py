from human.systems.cognitive.memory_management_system import MemoryManagementSystem
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:harvest_system.py
@说明:植物收获系统
@时间:2026/06/01
@作者:AI Assistant
@版本:1.0
'''

import math

from core.system import System
from core.world import World

from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.cognitive.memory_component import MemoryComponent
from resource.food.components.food_component import FoodComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem
from equipment.components.ownership_component import OwnershipComponent
from biology.organisms.plant.components.plant_component import PlantComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from resource.food.food_factory import FoodFactory
from resource.wood.wood_factory import WoodFactory
from human.systems.economy.economy_system import EconomySystem
from civilization.components.technology_modifier_component import TechnologyModifierComponent

import logging

logger = logging.getLogger(__name__)


class HarvestSystem(System):
    tick_interval = 1
    """
    植物收获系统。
    处理 ActionType.HARVEST 行为：
    1. 检查目标植物是否成熟可收获
    2. 计算收获量
    3. 创建食物实体放入背包
    4. 多年生植物保留并减少产量，一年生植物销毁
    """

    HARVEST_DISTANCE = 2  # 收获距离阈值
    HARVEST_DURATION = 1.0  # 收获耗时
    BASE_HARVEST_EFFICIENCY = 1.0  # 基础收获效率

    def update(self, world: World, dt: float = 1.0) -> None:
        for entity, (needs, action, inventory, task, space) in list(world.get_components(
            PhysiologyNeedsComponent, ActionComponent, InventoryComponent, TaskComponent, SpaceComponent
        )):
            if action.current_action != ActionType.HARVEST:
                continue
            self._process_harvest(world, entity, needs, action, inventory, task, space)

    def _process_harvest(self, world, entity, needs, action, inventory, task, space) -> None:
        """处理单个收获行为"""
        target_id = action.target_entity
        if target_id is None:
            self._fail(action, task, "无目标植物")
            return

        target_entity = world.query_entity(target_id)
        if target_entity is None:
            self._fail(action, task, "目标植物不存在")
            return

        plant_comp = world.get_component(target_entity, PlantComponent)
        lifecycle = world.get_component(target_entity, LifeCycleComponent)
        target_space = world.get_component(target_entity, SpaceComponent)
        morph = world.get_component(target_entity, MorphologyComponent)

        if plant_comp is None or lifecycle is None:
            self._fail(action, task, "目标不是可收获植物")
            return

        # 检查距离
        if target_space is not None:
            dist = math.hypot(space.x - target_space.x, space.y - target_space.y)
            if dist > self.HARVEST_DISTANCE:
                self._fail(action, task, f"距离过远 ({dist:.1f} > {self.HARVEST_DISTANCE})")
                return

        # 检查是否成熟
        if lifecycle.stage < plant_comp.harvest_stage:
            self._fail(action, task, "植物尚未成熟")
            return

        # 计算收获量（含技术加成）
        yield_amount = self._calculate_yield(plant_comp, morph) * self._get_harvest_multiplier(world)
        if yield_amount <= 0:
            self._fail(action, task, "无可收获量")
            return

        logger.debug(f"[Harvest] E{entity.id} 从植物 E{target_id} 收获了 {yield_amount:.1f}")

        # 创建收获物
        self._create_harvest_items(world, entity, space, plant_comp, yield_amount, target_entity)

        # 更新植物状态
        self._update_plant_state(world, plant_comp, morph, yield_amount, target_entity)

        # 记录记忆
        self._record_harvest_memory(world, entity, space, yield_amount, plant_comp)

        # 标记动作完成
        action.progress = 1.0
        action.status = ActionStatus.SUCCESS
        task.status = TaskStatus.DONE

    def _create_harvest_items(self, world, entity, space, plant_comp, yield_amount, target_entity) -> None:
        """创建收获物（食物+木材）"""
        food_type = plant_comp.yield_type
        food_entity = FoodFactory.create_food(
            world, space.x, space.y,
            food_type=food_type,
            amount=yield_amount * plant_comp.nutrition_per_unit
        )

        inventory = world.get_component(entity, InventoryComponent)
        if inventory:
            world.add_component(food_entity, OwnershipComponent(owner_id=entity.id))
            inventory.add(food_entity)

            space_system = world.get_system(SpaceSystem)
            if space_system is not None:
                space_system.remove_entity(food_entity.id)

        # 木材
        if plant_comp.produces_wood and plant_comp.wood_amount > 0:
            wood_entity = WoodFactory.create_wood(world, space.x, space.y)
            world.add_component(wood_entity, OwnershipComponent(owner_id=entity.id))
            inventory.add(wood_entity)
            if space_system is not None:
                space_system.remove_entity(wood_entity.id)
            logger.debug(f"[Harvest] E{entity.id} 从植物 E{target_entity.id} 收获了木材 x{plant_comp.wood_amount:.1f}")

        # 经济奖励
        EconomySystem.add_currency(world, entity, "gold", yield_amount * 0.1)

    def _update_plant_state(self, world, plant_comp, morph, yield_amount, target_entity) -> None:
        """更新植物收获后的状态"""
        if plant_comp.is_perennial:
            plant_comp.harvestable_yield = max(0.0, plant_comp.harvestable_yield - yield_amount)
            if morph is not None:
                morph.weight = max(0.0, morph.weight - yield_amount)
            logger.debug(f"[Harvest] E... 从植物 E{target_entity.id} 收获了 {yield_amount:.1f}（多年生保留）")
        else:
            world.remove_entity(target_entity)
            logger.debug(f"[Harvest] E... 从植物 E{target_entity.id} 收获了 {yield_amount:.1f}（一年生销毁）")

    def _record_harvest_memory(self, world, entity, space, yield_amount, plant_comp) -> None:
        """记录收获记忆"""
        memory = world.get_component(entity, MemoryComponent)
        if memory is None:
            return
        current_time = world.get_time().total_hours
        MemoryManagementSystem.add_event(memory, 
            current_time, "harvested_plant",
            f"在 ({space.x}, {space.y}) 收获了 {yield_amount:.1f} {plant_comp.yield_type}",
            impact=0.6,
            location=(space.x, space.y)
        )
        MemoryManagementSystem.record_place(memory, 
            (space.x, space.y), "food_source",
            current_time, sentiment=0.7
        )
        MemoryManagementSystem.record_success(memory, "harvest_plant")

    def _calculate_yield(self, plant_comp: PlantComponent, morph: MorphologyComponent | None) -> float:
        """计算实际收获量"""
        # 基于生物量计算
        if morph is not None:
            biomass_yield = morph.weight * 0.3  # 30% 生物量转化为可收获食物
        else:
            biomass_yield = 0.0

        # 取组件定义的最大产量和生物量计算的较小值
        yield_amount = min(plant_comp.harvestable_yield, biomass_yield)
        yield_amount = max(0.0, yield_amount)

        # 保底收获量（成熟植物至少能收获一点）
        if yield_amount < 1.0 and plant_comp.harvestable_yield > 0:
            yield_amount = min(plant_comp.harvestable_yield, 3.0)

        return yield_amount * self.BASE_HARVEST_EFFICIENCY

    def _get_harvest_multiplier(self, world: World) -> float:
        """读取文明技术带来的农业收获加成"""
        modifier = world.get_world_component(TechnologyModifierComponent)
        if modifier is not None and modifier.harvest_multiplier > 0:
            return modifier.harvest_multiplier
        return 1.0

    def _fail(self, action: ActionComponent, task: TaskComponent, reason: str) -> None:
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.FAILED
        action.progress = 0.0
        task.status = TaskStatus.FAILED
        logger.debug(f"[Harvest] 失败: {reason}")