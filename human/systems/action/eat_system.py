#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:eat_system.py
@说明:进食系统
@时间:2026/03/18 15:52:00
@作者:Sherry
@版本:1.1
'''

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


class EatSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
        进食系统
        仅负责处理 ActionType.EAT 行为。
        不执行额外寻食或状态切换逻辑。
    """

    def update(self, world: World, dt: float):
        space_system = world.get_system(SpaceSystem)
        for entity, (needs, action, inventory, task, space) in list(world.get_components(
            PhysiologyNeedsComponent, ActionComponent, InventoryComponent, TaskComponent, SpaceComponent
        )):
            needs: PhysiologyNeedsComponent
            action: ActionComponent
            inventory: InventoryComponent
            task: TaskComponent
            space: SpaceComponent

            if action.current_action != ActionType.EAT:
                continue

            food_entity, food_source = self._find_food(world, space_system, space, inventory)
            if food_entity is None:
                self._fail_action(action, task)
                continue

            food_component = world.get_component(food_entity, FoodComponent)
            if food_component is None:
                self._fail_action(action, task)
                continue

            self._consume_food(world, entity, needs, action, task, inventory, space, food_entity, food_component, food_source)

    def _find_food(self, world, space_system, space, inventory):
        """查找食物：先背包后地面，返回 (food_entity, food_source)"""
        food_entity = inventory.find(FoodComponent, world)
        if food_entity is not None:
            return food_entity, "inventory"

        if space_system is not None:
            for candidate_id in space_system.entities_at(space.x, space.y, space.layer):
                candidate = world.entities.get(candidate_id)
                if candidate is None:
                    continue
                if world.get_component(candidate, FoodComponent) is not None:
                    return candidate, "ground"

        return None, None

    def _fail_action(self, action: ActionComponent, task: TaskComponent):
        """标记进食动作失败"""
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.FAILED
        action.progress = 0.0
        task.status = TaskStatus.FAILED

    def _consume_food(self, world, entity, needs, action, task, inventory, space, food_entity, food_component, food_source):
        """执行进食并处理食物消耗、记忆记录"""
        needs.hunger = max(0.0, needs.hunger - food_component.nutrition)
        needs.thirst = max(0.0, needs.thirst - food_component.hydration)
        needs.energy = min(needs.max_energy, needs.energy + food_component.energy)

        food_component.amount -= food_component.bite_size
        if food_component.amount <= 0:
            if food_source == "inventory":
                inventory.remove(food_entity)

            ownership = world.get_component(food_entity, OwnershipComponent)
            if ownership is not None:
                ownership.release_ownership()

            world.remove_entity(food_entity)

        memory = world.get_component(entity, MemoryComponent)
        current_time = world.get_time().total_hours
        if memory:
            memory.add_event(
                current_time, "found_food",
                f"在 ({space.x}, {space.y}) 进食",
                impact=0.5,
                location=(space.x, space.y)
            )
            memory.record_place(
                (space.x, space.y), "food_source",
                current_time, sentiment=0.6
            )
            memory.record_success("find_food")

        action.progress = 1.0
        action.status = ActionStatus.SUCCESS
        task.status = TaskStatus.DONE



