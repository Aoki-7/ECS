#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:resource_gathering_system.py
@说明:资源采集系统 - 人类采集环境资源的系统
@时间:2026/04/18 10:00:00
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World
from core.entity import Entity
from typing import List, Tuple

from core.components.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.abilities.skill_component import SkillComponent
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from space.space_component import SpaceComponent
from resource.components.resource_component import ResourceComponent, ResourceState
from environment.environment_component import EnvironmentComponent


class ResourceGatheringSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    资源采集系统

    功能：
    - 人类可以采集环境中的资源（食物、水、木材、石材、金属）
    - 采集效率受技能影响
    - 采集行为消耗能量
    - 资源采集后进入人类库存
    """

    def update(self, world: World, dt: float) -> None:
        """更新资源采集行为"""
        # 先查询最核心的 2 个组件，其余在循环内补查
        for entity, (action, task) in world.get_components(
            ActionComponent, TaskComponent
        ):
            if action.current_action != ActionType.GATHER:
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

            # 检查是否有足够的能量进行采集
            if needs.energy < 10.0:
                action.status = ActionStatus.FAILED
                task.status = TaskStatus.FAILED
                continue

            # 查找附近的资源
            nearby_resources = self._find_nearby_resources(world, space.position, 5.0)

            if not nearby_resources:
                action.status = ActionStatus.FAILED
                task.status = TaskStatus.FAILED
                continue

            # 选择最佳资源进行采集
            target_resource, resource_entity = self._select_best_resource(nearby_resources, skill)

            if not target_resource:
                action.status = ActionStatus.FAILED
                task.status = TaskStatus.FAILED
                continue

            # 执行采集
            self._perform_gathering(entity, target_resource, resource_entity,
                                  inventory, skill, needs, world, dt)

            # 完成采集任务
            action.status = ActionStatus.COMPLETED
            task.status = TaskStatus.COMPLETED

    def _find_nearby_resources(self, world: World, position: Tuple[float, float, float],
                             radius: float) -> List[Tuple[ResourceComponent, Entity]]:
        """查找附近的资源"""
        nearby_resources = []

        for resource_entity, resource in world.get_components(ResourceComponent):
            resource_space = world.get_component(resource_entity, SpaceComponent)
            if not resource_space:
                continue

            # 计算距离
            distance = ((position[0] - resource_space.position[0]) ** 2 +
                       (position[1] - resource_space.position[1]) ** 2 +
                       (position[2] - resource_space.position[2]) ** 2) ** 0.5

            if distance <= radius and resource.state == ResourceState.AVAILABLE:
                nearby_resources.append((resource, resource_entity))

        return nearby_resources

    def _select_best_resource(self, resources: List[Tuple[ResourceComponent, Entity]],
                            skill: SkillComponent) -> Tuple[ResourceComponent, Entity]:
        """选择最佳采集资源"""
        if not resources:
            return None, None

        # 优先选择高质量、可再生资源
        best_score = -1
        best_resource = None
        best_entity = None

        gathering_skill = skill.skills.get('gathering', 1.0)

        for resource, entity in resources:
            score = (resource.quality * 0.4 +
                    (1.0 if resource.regenerable else 0.0) * 0.3 +
                    min(resource.amount / resource.max_amount, 1.0) * 0.3)

            # 技能加成
            score *= (0.5 + gathering_skill * 0.1)

            if score > best_score:
                best_score = score
                best_resource = resource
                best_entity = entity

        return best_resource, best_entity

    def _perform_gathering(self, entity, target_resource: ResourceComponent,
                          resource_entity, inventory: InventoryComponent,
                          skill: SkillComponent, needs: PhysiologyNeedsComponent,
                          world: World, dt: float):
        """执行采集行为"""
        gathering_skill = skill.skills.get('gathering', 1.0)

        # 计算采集效率
        base_efficiency = 5.0  # 基础采集量
        efficiency = base_efficiency * (0.5 + gathering_skill * 0.1)

        # 限制采集量不超过资源总量
        gather_amount = min(efficiency * dt, target_resource.amount)

        if gather_amount <= 0:
            return

        # 消耗能量
        energy_cost = gather_amount * 0.1
        needs.energy = max(0.0, needs.energy - energy_cost)

        # 从资源中移除
        target_resource.amount -= gather_amount

        # 添加到人类库存
        resource_type = target_resource.resource_type
        if resource_type == 'food':
            inventory.add_food(gather_amount, target_resource.quality)
        elif resource_type == 'water':
            inventory.add_water(gather_amount, target_resource.quality)
        elif resource_type == 'wood':
            inventory.add_wood(gather_amount, target_resource.quality)
        elif resource_type == 'stone':
            inventory.add_stone(gather_amount, target_resource.quality)
        elif resource_type == 'metal':
            inventory.add_metal(gather_amount, target_resource.quality)

        # 记录经验
        self._record_gathering_experience(entity, resource_type, gather_amount, world)

    def _record_gathering_experience(self, entity, resource_type: str,
                                   amount: float, world: World):
        """记录采集经验"""
        memory = world.get_component(entity, MemoryComponent)
        if memory:
            memory.add_experience({
                'type': 'skill_practice',
                'skill_type': 'gathering',
                'resource_type': resource_type,
                'amount': amount,
                'timestamp': world.get_component(entity, TimeComponent).current_time if world.get_component(entity, TimeComponent) else 0
            })