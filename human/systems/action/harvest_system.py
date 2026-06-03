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
from core.components.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.cognitive.memory_component import MemoryComponent
from resource.food.components.food_component import FoodComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem
from equipment.components.ownership_component import OwnershipComponent
from plant.components.plant_component import PlantComponent
from biology.components.life_cycle_component import LifeCycleComponent
from biology.components.morphology_component import MorphologyComponent
from resource.food.food_factory import FoodFactory
from resource.wood.wood_factory import WoodFactory

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

            target_id = action.target_entity
            if target_id is None:
                self._fail(action, task, "无目标植物")
                continue

            target_entity = world.query_entity(target_id)
            if target_entity is None:
                self._fail(action, task, "目标植物不存在")
                continue

            plant_comp = world.get_component(target_entity, PlantComponent)
            lifecycle = world.get_component(target_entity, LifeCycleComponent)
            target_space = world.get_component(target_entity, SpaceComponent)
            morph = world.get_component(target_entity, MorphologyComponent)

            if plant_comp is None or lifecycle is None:
                self._fail(action, task, "目标不是可收获植物")
                continue

            # 检查距离
            if target_space is not None:
                dist = math.hypot(space.x - target_space.x, space.y - target_space.y)
                if dist > self.HARVEST_DISTANCE:
                    self._fail(action, task, f"距离过远 ({dist:.1f} > {self.HARVEST_DISTANCE})")
                    continue

            # 检查是否成熟
            if lifecycle.stage < plant_comp.harvest_stage:
                self._fail(action, task, "植物尚未成熟")
                continue

            # 计算收获量
            yield_amount = self._calculate_yield(plant_comp, morph)
            if yield_amount <= 0:
                self._fail(action, task, "无可收获量")
                continue

            # 创建食物实体
            food_type = plant_comp.yield_type
            food_entity = FoodFactory.create_food(
                world, space.x, space.y,
                food_type=food_type,
                amount=yield_amount * plant_comp.nutrition_per_unit
            )

            # 设置所有权并放入背包
            world.add_component(food_entity, OwnershipComponent(owner_id=entity.id))
            inventory.add(food_entity)

            # 从空间索引移除（背包中的物品不应在地面）
            space_system = world.get_system(SpaceSystem)
            if space_system is not None:
                space_system.remove_entity(food_entity)

            # 如果植物产出木材，同时创建木材实体
            if plant_comp.produces_wood and plant_comp.wood_amount > 0:
                wood_entity = WoodFactory.create_wood(world, space.x, space.y)
                world.add_component(wood_entity, OwnershipComponent(owner_id=entity.id))
                inventory.add(wood_entity)
                if space_system is not None:
                    space_system.remove_entity(wood_entity)
                logger.debug(f"[Harvest] E{entity.id} 从植物 E{target_entity.id} 收获了木材 x{plant_comp.wood_amount:.1f}")

            # 更新植物状态
            if plant_comp.is_perennial:
                # 多年生：减少可收获量，保留实体
                plant_comp.harvestable_yield = max(0.0, plant_comp.harvestable_yield - yield_amount)
                if morph is not None:
                    morph.weight = max(0.0, morph.weight - yield_amount)
                logger.debug(f"[Harvest] E{entity.id} 从植物 E{target_entity.id} 收获了 {yield_amount:.1f} {food_type}（多年生保留）")
            else:
                # 一年生：销毁实体
                world.remove_entity(target_entity)
                logger.debug(f"[Harvest] E{entity.id} 从植物 E{target_entity.id} 收获了 {yield_amount:.1f} {food_type}（一年生销毁）")

            # 记录记忆
            memory = world.get_component(entity, MemoryComponent)
            current_time = world.get_time().total_hours
            if memory:
                memory.add_event(
                    current_time, "harvested_plant",
                    f"在 ({space.x}, {space.y}) 收获了 {yield_amount:.1f} {food_type}",
                    impact=0.6,
                    location=(space.x, space.y)
                )
                memory.record_place(
                    (space.x, space.y), "food_source",
                    current_time, sentiment=0.7
                )
                memory.record_success("harvest_plant")

            # 标记动作完成
            action.progress = 1.0
            action.status = ActionStatus.SUCCESS
            task.status = TaskStatus.DONE

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

    def _fail(self, action: ActionComponent, task: TaskComponent, reason: str) -> None:
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.FAILED
        action.progress = 0.0
        task.status = TaskStatus.FAILED
        logger.debug(f"[Harvest] 失败: {reason}")
