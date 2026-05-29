#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:construction_system.py
@说明:建造系统 - 人类建造建筑和工具的系统
@时间:2026/04/18 10:00:00
@作者:Sherry
@版本:1.0
'''

import logging

from core.system import System
from core.world import World
from typing import Dict, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.abilities.skill_component import SkillComponent
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from space.space_component import SpaceComponent
from equipment.equipment_factory import EquipmentFactory


class BuildingType(Enum):
    """建筑类型枚举"""
    HUT = "hut"           # 棚屋
    WORKSHOP = "workshop" # 工坊
    STORAGE = "storage"   # 仓库
    FARM = "farm"         # 农场


class ToolType(Enum):
    """工具类型枚举"""
    AXE = "axe"           # 斧头
    PICKAXE = "pickaxe"   # 镐
    KNIFE = "knife"       # 刀
    SPEAR = "spear"       # 矛


class ConstructionSystem(System):
    """
    建造系统

    功能：
    - 建造建筑（棚屋、工坊、仓库、农场）
    - 制造工具（斧头、镐、刀、矛）
    - 建造效率受技能影响
    - 建造消耗资源和能量
    """

    # 建造配方
    BUILDING_RECIPES = {
        BuildingType.HUT: {
            'wood': 20.0,
            'stone': 10.0,
            'time': 24.0  # 小时
        },
        BuildingType.WORKSHOP: {
            'wood': 30.0,
            'stone': 20.0,
            'metal': 5.0,
            'time': 48.0
        },
        BuildingType.STORAGE: {
            'wood': 15.0,
            'stone': 25.0,
            'time': 36.0
        },
        BuildingType.FARM: {
            'wood': 10.0,
            'stone': 5.0,
            'time': 18.0
        }
    }

    # 工具配方
    TOOL_RECIPES = {
        ToolType.AXE: {
            'wood': 5.0,
            'stone': 2.0,
            'time': 4.0
        },
        ToolType.PICKAXE: {
            'wood': 3.0,
            'stone': 5.0,
            'metal': 2.0,
            'time': 6.0
        },
        ToolType.KNIFE: {
            'stone': 3.0,
            'metal': 1.0,
            'time': 2.0
        },
        ToolType.SPEAR: {
            'wood': 8.0,
            'stone': 2.0,
            'metal': 1.0,
            'time': 5.0
        }
    }

    def update(self, world: World, dt: float):
        """更新建造行为"""
        # 先查询最核心的 2 个组件，其余在循环内补查
        for entity, (action, task) in world.get_components(
            ActionComponent, TaskComponent
        ):
            if action.current_action not in [ActionType.BUILD, ActionType.CRAFT]:
                continue

            if action.status != ActionStatus.IN_PROGRESS:
                continue

            # 补查其他组件
            inventory = world.get_component(entity, InventoryComponent)
            skill = world.get_component(entity, SkillComponent)
            needs = world.get_component(entity, PhysiologyNeedsComponent)
            space = world.get_component(entity, SpaceComponent)

            if not (inventory and skill and needs and space):
                continue

            # 检查是否有足够的能量
            if needs.energy < 15.0:
                action.status = ActionStatus.FAILED
                task.status = TaskStatus.FAILED
                continue

            if action.current_action == ActionType.BUILD:
                self._perform_building(entity, action, inventory, skill, task, needs, space, world, dt)
            elif action.current_action == ActionType.CRAFT:
                self._perform_crafting(entity, action, inventory, skill, task, needs, world, dt)

    def _perform_building(self, entity, action: ActionComponent, inventory: InventoryComponent,
                         skill: SkillComponent, task: TaskComponent, needs: PhysiologyNeedsComponent,
                         space: SpaceComponent, world: World, dt: float):
        """执行建造"""
        building_type = getattr(action, 'target_type', None)
        if not building_type or building_type not in self.BUILDING_RECIPES:
            action.status = ActionStatus.FAILED
            task.status = TaskStatus.FAILED
            return

        recipe = self.BUILDING_RECIPES[building_type]
        construction_skill = skill.skills.get('construction', 1.0)

        # 检查材料是否足够
        if not self._check_materials(inventory, recipe):
            action.status = ActionStatus.FAILED
            task.status = TaskStatus.FAILED
            return

        # 初始化建造进度
        if not hasattr(action, 'progress'):
            action.progress = 0.0
            action.total_time = recipe['time'] / (0.5 + construction_skill * 0.1)

        # 消耗能量
        energy_cost = dt * 2.0
        needs.energy = max(0.0, needs.energy - energy_cost)

        # 推进建造进度
        action.progress += dt

        if action.progress >= action.total_time:
            # 建造完成
            self._complete_building(entity, building_type, recipe, inventory, space, world)
            action.status = ActionStatus.COMPLETED
            task.status = TaskStatus.COMPLETED
            self._record_construction_experience(entity, 'building', building_type.value, world)

    def _perform_crafting(self, entity, action: ActionComponent, inventory: InventoryComponent,
                         skill: SkillComponent, task: TaskComponent, needs: PhysiologyNeedsComponent,
                         world: World, dt: float):
        """执行制造"""
        tool_type = getattr(action, 'target_type', None)
        if not tool_type or tool_type not in self.TOOL_RECIPES:
            action.status = ActionStatus.FAILED
            task.status = TaskStatus.FAILED
            return

        recipe = self.TOOL_RECIPES[tool_type]
        crafting_skill = skill.skills.get('crafting', 1.0)

        # 检查材料是否足够
        if not self._check_materials(inventory, recipe):
            action.status = ActionStatus.FAILED
            task.status = TaskStatus.FAILED
            return

        # 初始化制造进度
        if not hasattr(action, 'progress'):
            action.progress = 0.0
            action.total_time = recipe['time'] / (0.5 + crafting_skill * 0.1)

        # 消耗能量
        energy_cost = dt * 1.5
        needs.energy = max(0.0, needs.energy - energy_cost)

        # 推进制造进度
        action.progress += dt

        if action.progress >= action.total_time:
            # 制造完成
            self._complete_crafting(entity, tool_type, recipe, inventory, world)
            action.status = ActionStatus.COMPLETED
            task.status = TaskStatus.COMPLETED
            self._record_construction_experience(entity, 'crafting', tool_type.value, world)

    def _check_materials(self, inventory: InventoryComponent, recipe: Dict[str, float]) -> bool:
        """检查材料是否足够"""
        for material, amount in recipe.items():
            if material == 'time':
                continue
            if material == 'wood' and inventory.wood < amount:
                return False
            if material == 'stone' and inventory.stone < amount:
                return False
            if material == 'metal' and inventory.metal < amount:
                return False
        return True

    def _complete_building(self, entity, building_type: BuildingType, recipe: Dict[str, float],
                          inventory: InventoryComponent, space: SpaceComponent, world: World):
        """完成建造"""
        # 消耗材料
        for material, amount in recipe.items():
            if material == 'time':
                continue
            if material == 'wood':
                inventory.wood -= amount
            elif material == 'stone':
                inventory.stone -= amount
            elif material == 'metal':
                inventory.metal -= amount

        # 创建建筑实体
        building_entity = world.create_entity()

        # 添加建筑组件（这里需要扩展建筑组件）
        # TODO: 创建建筑组件系统

        logger.info(f"[ConstructionSystem] Built {building_type.value} at position {space.position}")

    def _complete_crafting(self, entity, tool_type: ToolType, recipe: Dict[str, float],
                          inventory: InventoryComponent, world: World):
        """完成制造"""
        # 消耗材料
        for material, amount in recipe.items():
            if material == 'time':
                continue
            if material == 'wood':
                inventory.wood -= amount
            elif material == 'stone':
                inventory.stone -= amount
            elif material == 'metal':
                inventory.metal -= amount

        # 创建工具实体
        tool_entity = EquipmentFactory.create_tool(tool_type.value, world)

        # 将工具添加到人类库存
        inventory.add_equipment(tool_entity)

        logger.info(f"[ConstructionSystem] Crafted {tool_type.value}")

    def _record_construction_experience(self, entity, skill_type: str, target_type: str, world: World):
        """记录建造/制造经验"""
        memory = world.get_component(entity, MemoryComponent)
        if memory:
            memory.add_experience({
                'type': 'skill_practice',
                'skill_type': skill_type,
                'target_type': target_type,
                'timestamp': world.get_component(entity, TimeComponent).current_time if world.get_component(entity, TimeComponent) else 0
            })