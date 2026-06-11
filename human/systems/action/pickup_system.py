#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:pickup_system.py
@说明:获取功能系统
@时间:2026/03/19 17:18:39
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World

from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from equipment.components.ownership_component import OwnershipComponent


class PickupSystem(System):
    tick_interval = 1  # 每帧执行一次，避免拾取动作延迟导致资源获取滞后
    """
        拾取系统
        属于Action系统的一部分，负责处理拾取行为。
        逻辑：
        1. 检测当前Action是否为PICKUP
        2. 检查目标实体是否存在且在附近（距离 <= 1）
        3. 检查库存空间
        4. 处理拾取进度
        5. 将目标实体添加到InventoryComponent
        6. 为目标实体添加或更新OwnershipComponent，设置所有者
        7. 物品保留在World中（不被移除），但标记为已被拥有
        
        新设计理念：
        - 物品被拾取后不从World移除，而是标记所有权
        - 通过OwnershipComponent标记所有者
        - 其他实体无法直接观察或交互被拥有的物品
    """
    
    # 拾取距离
    PICKUP_DISTANCE = 1
    # 拾取所需时间（秒）
    PICKUP_DURATION = 0.5
    
    def update(self, world: World, dt: float):
        for picker_entity, (action, space, inventory) in list(world.get_components(ActionComponent, SpaceComponent, InventoryComponent)):
            action: ActionComponent
            space: SpaceComponent
            inventory: InventoryComponent

            if action.current_action != ActionType.PICKUP:
                continue

            target_entity = self._validate_target(world, action, space)
            if target_entity is None:
                continue

            if len(inventory.items) >= inventory.capacity:
                self._fail_pickup(action)
                continue

            action.progress += dt / self.PICKUP_DURATION
            if action.progress < 1.0:
                action.status = ActionStatus.RUNNING
                continue

            self._complete_pickup(world, picker_entity, action, inventory, target_entity)

    def _validate_target(self, world, action: ActionComponent, space: SpaceComponent):
        """验证拾取目标：存在性、距离"""
        target_entity_id = action.target_entity
        if target_entity_id is None:
            self._fail_pickup(action)
            return None

        target_entity = world.query_entity(target_entity_id)
        if target_entity is None:
            self._fail_pickup(action, clear_target=True)
            return None

        target_space = world.get_component(target_entity, SpaceComponent)
        if target_space is None:
            self._fail_pickup(action, clear_target=True)
            return None

        if self._calculate_distance(space, target_space) > self.PICKUP_DISTANCE:
            self._fail_pickup(action)
            return None

        return target_entity

    def _fail_pickup(self, action: ActionComponent, clear_target: bool = False):
        """标记拾取失败"""
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.FAILED
        action.progress = 0.0
        if clear_target:
            action.target_entity = None

    def _complete_pickup(self, world, picker_entity, action: ActionComponent, inventory, target_entity):
        """完成拾取：添加所有权、从空间索引移除"""
        if inventory.add(target_entity):
            ownership = world.get_component(target_entity, OwnershipComponent)
            if ownership is None:
                ownership = OwnershipComponent()
                world.add_component(target_entity, ownership)
            ownership.set_owner(picker_entity)

            space_system = world.get_system(SpaceSystem)
            if space_system is not None:
                space_system.remove_entity(target_entity.id)

            action.progress = 1.0
            action.target_entity = None
        else:
            action.status = ActionStatus.FAILED
            action.progress = 0.0
            action.target_entity = None
    
    # ===== 辅助方法 =====
    
    @staticmethod
    def _calculate_distance(pos1: SpaceComponent, pos2: SpaceComponent) -> float:
        """计算两个位置之间的曼哈顿距离"""
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)