from human.systems.cognitive.memory_management_system import MemoryManagementSystem
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

from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

from resource.water.components.water_component import WaterComponent
from resource.components.resource_component import ResourceComponent


class DrinkSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
        饮水系统
        仅负责处理 ActionType.DRINK 行为。
        支持从背包或地面上同位置的水源饮水。
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

            if action.current_action != ActionType.DRINK:
                continue

            water_entity, water_source = self._find_water(world, space_system, space, inventory)

            if water_entity is None:
                self._fail_action(action, task)
                continue

            water_component = world.get_component(water_entity, WaterComponent)
            if water_component is None or water_component.amount <= 0:
                self._fail_action(action, task)
                continue

            action.progress += dt * 1.0

            if action.progress >= 1.0:
                self._finish_drinking(world, entity, needs, action, task, inventory, space, water_entity, water_component, water_source)

    def _find_water(self, world, space_system, space, inventory):
        """从背包和地面搜索水源，返回 (water_entity, water_source)"""
        # 防御：InventoryComponent 可能没有 find 方法
        if hasattr(inventory, 'find'):
            water_entity = inventory.find(WaterComponent, world)
        else:
            water_entity = None
            if hasattr(inventory, 'items'):
                for item_id in inventory.items:
                    if world.get_component(item_id, WaterComponent) is not None:
                        water_entity = item_id
                        break
        if water_entity is not None:
            return water_entity, "inventory"

        # 使用空间索引 neighbors() O(9) 查询周围水源
        if space_system is not None:
            best_dist = float("inf")
            for candidate_id in space_system.neighbors(space.x, space.y, 5, space.layer):
                candidate = world.entities.get(candidate_id)
                if candidate is None:
                    continue
                water_comp = world.get_component(candidate, WaterComponent)
                if water_comp is None:
                    continue
                c_space = world.get_component(candidate, SpaceComponent)
                if c_space is None:
                    continue
                dist = abs(c_space.x - space.x) + abs(c_space.y - space.y)
                if dist < best_dist:
                    best_dist = dist
                    water_entity = candidate

            if water_entity is not None:
                return water_entity, "ground"

        # 兜底：空间索引未命中时，遍历所有地面水源
        best_dist = float("inf")
        for w_ent, (w_comp, w_space) in list(world.get_components(WaterComponent, SpaceComponent)):
            if w_comp.amount <= 0:
                continue
            d = abs(w_space.x - space.x) + abs(w_space.y - space.y)
            if d < best_dist:
                best_dist = d
                water_entity = w_ent

        return water_entity, "ground" if water_entity is not None else None

    def _fail_action(self, action: ActionComponent, task: TaskComponent):
        """标记动作失败"""
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.FAILED
        action.progress = 0.0
        task.status = TaskStatus.FAILED

    def _finish_drinking(self, world, entity, needs, action, task, inventory, space, water_entity, water_component, water_source):
        """饮水完成处理"""
        water_component.drink()
        needs.thirst = max(0, needs.thirst - 50)

        if water_component.amount <= 0:
            if water_source == "inventory":
                # 防御：InventoryComponent 可能没有 remove 方法
                if hasattr(inventory, 'remove'):
                    inventory.remove(water_entity)
                elif hasattr(inventory, 'items') and isinstance(inventory.items, dict):
                    if water_entity in inventory.items:
                        del inventory.items[water_entity]
                        inventory.current_weight -= getattr(water_component, 'amount', 0)
            world.remove_entity(water_entity)

        memory = world.get_component(entity, MemoryComponent)
        time_obj = world.get_time()
        current_time = time_obj.total_hours if time_obj else 0.0
        if memory:
            MemoryManagementSystem.add_event(memory, 
                current_time, "found_water",
                f"在 ({space.x}, {space.y}) 饮水",
                impact=0.5,
                location=(space.x, space.y)
            )
            MemoryManagementSystem.record_place(memory, 
                (space.x, space.y), "water_source",
                current_time, sentiment=0.7
            )
            MemoryManagementSystem.record_success(memory, "find_water")

        action.progress = 1.0
        action.status = ActionStatus.SUCCESS
        task.status = TaskStatus.DONE
