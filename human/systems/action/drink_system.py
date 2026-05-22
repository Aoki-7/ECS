#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:drink_system.py
@说明:饮水系统
@时间:2026/04/13
@作者:GitHub Copilot
@版本:1.1
'''

from core.system import System
from core.world import World

from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from space.space_component import SpaceComponent

from resource.water.components.water_component import WaterComponent
from resource.components.resource_component import ResourceComponent


class DrinkSystem(System):
    """
        饮水系统
        仅负责处理 ActionType.DRINK 行为。
        支持从背包或地面上同位置的水源饮水。
    """

    def update(self, world: World, dt):
        for entity, (needs, action, inventory, task, space) in world.get_components(
            PhysiologyNeedsComponent, ActionComponent, InventoryComponent, TaskComponent, SpaceComponent
        ):
            needs: PhysiologyNeedsComponent
            action: ActionComponent
            inventory: InventoryComponent
            task: TaskComponent
            space: SpaceComponent

            if action.current_action != ActionType.DRINK:
                continue

            water_entity = None

            # 先从inventory找水
            water_entity = inventory.find(WaterComponent, world)
            water_source = "inventory"

            # 再从地面同位置找水
            if water_entity is None:
                for w_ent, (w_comp, w_space) in world.get_components(WaterComponent, SpaceComponent):
                    if w_space.x == space.x and w_space.y == space.y and w_space.layer == space.layer:
                        water_entity = w_ent
                        water_source = "ground"
                        break

            if water_entity is None:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                task.status = TaskStatus.FAILED
                continue

            water_component = world.get_component(water_entity, WaterComponent)
            if water_component is None or water_component.amount <= 0:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                task.status = TaskStatus.FAILED
                continue

            # 模拟饮水过程
            action.progress += dt * 1.0

            if action.progress >= 1.0:
                # 饮水完成
                sip = water_component.drink()
                needs.thirst = max(0, needs.thirst - 50)

                # 仅当水量耗尽时才从背包移除或销毁实体
                if water_component.amount <= 0:
                    if water_source == "inventory":
                        inventory.remove(water_entity)
                    world.remove_entity(water_entity)

                action.progress = 1.0
                task.status = TaskStatus.DONE
