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
from core.components.action_component import ActionComponent, ActionType, ActionStatus
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

            water_entity = None

            # 先从inventory找水
            water_entity = inventory.find(WaterComponent, world)
            water_source = "inventory" if water_entity is not None else None

            # 使用空间索引 neighbors() O(9) 查询周围水源，替代 O(W) 全量扫描
            if water_entity is None and space_system is not None:
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
                        water_source = "ground"

            # 兜底：空间索引未命中时，遍历所有地面水源
            if water_entity is None:
                best_dist = float("inf")
                for w_ent, (w_comp, w_space) in list(world.get_components(WaterComponent, SpaceComponent)):
                    if w_comp.amount <= 0:
                        continue
                    d = abs(w_space.x - space.x) + abs(w_space.y - space.y)
                    if d < best_dist:
                        best_dist = d
                        water_entity = w_ent
                        water_source = "ground"

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

                # 记录成功到记忆
                memory = world.get_component(entity, MemoryComponent)
                current_time = world.get_time().total_hours
                if memory:
                    memory.add_event(
                        current_time, "found_water",
                        f"在 ({space.x}, {space.y}) 饮水",
                        impact=0.5,
                        location=(space.x, space.y)
                    )
                    memory.record_place(
                        (space.x, space.y), "water_source",
                        current_time, sentiment=0.7
                    )
                    memory.record_success("find_water")

                action.progress = 1.0
                action.status = ActionStatus.SUCCESS
                task.status = TaskStatus.DONE
