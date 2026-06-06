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

            food_entity = None
            food_source = None

            # 先从inventory找食物
            food_entity = inventory.find(FoodComponent, world)
            if food_entity is not None:
                food_source = "inventory"
            else:
                # 使用空间索引 O(1) 查询同坐标食物，替代 O(F) 全量扫描
                if space_system is not None:
                    for candidate_id in space_system.entities_at(space.x, space.y, space.layer):
                        candidate = world.entities.get(candidate_id)
                        if candidate is None:
                            continue
                        food_comp = world.get_component(candidate, FoodComponent)
                        if food_comp is not None:
                            food_entity = candidate
                            food_source = "ground"
                            break
            
            if food_entity is None:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                task.status = TaskStatus.FAILED
                continue

            food_component: FoodComponent = world.get_component(food_entity, FoodComponent)

            if food_component is None:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                task.status = TaskStatus.FAILED
                continue

            needs.hunger = max(0.0, needs.hunger - food_component.nutrition)
            needs.thirst = max(0.0, needs.thirst - food_component.hydration)
            needs.energy = min(needs.max_energy, needs.energy + food_component.energy)

            food_component.amount -= food_component.bite_size
            if food_component.amount <= 0:
                # 食物消耗完毕，从背包移除并销毁实体
                if food_source == "inventory":
                    inventory.remove(food_entity)
                
                # 释放所有权
                ownership: OwnershipComponent | None = world.get_component(food_entity, OwnershipComponent)
                if ownership is not None:
                    ownership.release_ownership()
                
                # 销毁已消耗的食物实体，防止僵尸实体泄漏
                world.remove_entity(food_entity)

            # 记录成功到记忆
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

            # 标记动作完成
            action.progress = 1.0
            action.status = ActionStatus.SUCCESS
            task.status = TaskStatus.DONE



