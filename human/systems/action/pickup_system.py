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

from core.components.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from equipment.components.ownership_component import OwnershipComponent


class PickupSystem(System):
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
    
    def update(self, world: World, dt):
        for picker_entity, (action, space, inventory) in world.get_components(ActionComponent, SpaceComponent, InventoryComponent):
            action: ActionComponent
            space: SpaceComponent
            inventory: InventoryComponent
            
            # 检查当前动作是否为拾取
            if action.current_action != ActionType.PICKUP:
                continue
            
            # ===== 获取目标 =====
            target_entity_id = action.target_entity
            
            if target_entity_id is None:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                continue
            
            # 检查目标是否还存在
            target_entity = world.query_entity(target_entity_id)
            if target_entity is None:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                action.target_entity = None
                continue
            
            # ===== 检查距离 =====
            target_space = world.get_component(target_entity, SpaceComponent)
            if target_space is None:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                action.target_entity = None
                continue
            
            distance = self._calculate_distance(space, target_space)
            
            if distance > self.PICKUP_DISTANCE:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                continue
            
            # ===== 检查库存空间 =====
            if len(inventory.items) >= inventory.capacity:
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                continue
            
            # ===== 处理拾取进度 =====
            action.progress += dt / self.PICKUP_DURATION
            
            if action.progress < 1.0:
                action.status = ActionStatus.RUNNING
                continue
            
            # ===== 拾取完成 =====
            if inventory.add(target_entity):
                # 为物品添加OwnershipComponent（如果没有的话）
                ownership = world.get_component(target_entity, OwnershipComponent)
                if ownership is None:
                    ownership = OwnershipComponent()
                    world.add_component(target_entity, ownership)
                
                # 设置物品所有者为拾取者
                ownership.set_owner(picker_entity)
                
                # 从空间索引中移除，防止被重复拾取
                space_system = world.get_system(SpaceSystem)
                if space_system is not None:
                    space_system.remove_entity(target_entity.id)
                
                # 标记完成，由 ActionSystem 处理
                action.progress = 1.0
                action.target_entity = None
            else:
                # 库存已满，拾取失败
                action.status = ActionStatus.FAILED
                action.progress = 0.0
                action.target_entity = None
    
    # ===== 辅助方法 =====
    
    @staticmethod
    def _calculate_distance(pos1: SpaceComponent, pos2: SpaceComponent) -> float:
        """计算两个位置之间的曼哈顿距离"""
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)