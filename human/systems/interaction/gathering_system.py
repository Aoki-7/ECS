#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:gathering_system.py
@说明:采集系统
@时间:2026/03/15 22:54:08
@作者:Sherry
@版本:2.0
'''

from core.system import System
from core.world import World
from human.components.interaction.gathering_component import GatheringComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from resource.components.resource_component import ResourceComponent
from space.space_component import SpaceComponent
import math


class GatheringSystem(System):
    """
    采集系统
    
    负责处理人类从环境中采集资源的行为。
    - 检测附近的资源
    - 执行采集操作
    - 更新库存和资源数量
    """
    
    GATHER_RADIUS = 5.0  # 采集范围（单位：空间距离）
    GATHER_RATE = 10.0   # 每秒采集速率（单位：资源量/秒）

    def update(self, world: World, dt: float):
        """
        每帧更新采集状态
        
        Args:
            world: World实例
            dt: 时间增量（秒）
        """
        # 获取所有具有采集行动的实体
        for entity, (action, gathering, space) in world.get_components(
            ActionComponent, GatheringComponent, SpaceComponent
        ):
            if action.current_action == ActionType.GATHER and action.status == ActionStatus.RUNNING:
                self._process_gathering(world, entity, action, gathering, space, dt)
    
    def _process_gathering(self, world: World, entity, action: ActionComponent, gathering: GatheringComponent, 
                          space: SpaceComponent, dt: float):
        """
        处理单个实体的采集操作
        
        Args:
            world: World实例
            entity: 采集者实体
            action: 行动组件
            gathering: 采集组件
            space: 空间组件
            dt: 时间增量
        """
        # 查询附近的资源
        nearby_resources = self._find_nearby_resources(
            world, space, gathering.resource_type, self.GATHER_RADIUS
        )
        
        if not nearby_resources:
            # 没有找到资源，设置行动失败
            action.status = ActionStatus.FAILED
            return
        
        # 对每个附近的资源执行采集
        for resource_entity, resource, resource_space in nearby_resources:
            gathered_amount = min(
                resource.amount,
                self.GATHER_RATE * dt
            )
            
            # 更新采集组件
            gathering.gather(gathering.resource_type, gathered_amount)
            
            # 减少资源数量
            resource.amount -= gathered_amount
            
            # 如果资源耗尽，移除资源实体
            if resource.amount <= 0:
                world.remove_entity(resource_entity)
            
            break  # 只从一个资源源采集
    
    def _find_nearby_resources(self, world: World, space: SpaceComponent, 
                              resource_type: str, radius: float) -> list:
        """
        查找附近的指定类型资源
        
        Args:
            world: World实例
            space: 采集者的空间位置
            resource_type: 要采集的资源类型
            radius: 搜索半径
            
        Returns:
            list: [(resource_entity, resource_component, resource_space), ...]
        """
        nearby = []
        
        # 遍历所有资源实体
        for entity, (resource, res_space) in world.get_components(
            ResourceComponent, SpaceComponent
        ):
            # 检查资源类型是否匹配
            if resource.resource_type != resource_type:
                continue
            
            # 计算距离
            dx = res_space.x - space.x
            dy = res_space.y - space.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # 如果在范围内，添加到列表
            if distance <= radius:
                nearby.append((entity, resource, res_space))
        
        return nearby
