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
from civilization.components.technology_modifier_component import TechnologyModifierComponent
import math


class GatheringSystem(System):
    tick_interval = 5  # 每5帧执行一次
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
        for entity, (action, gathering, space) in list(world.get_components(
            ActionComponent, GatheringComponent, SpaceComponent
        )):
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
        
        # 对每个附近的资源执行采集（含技术加成）
        for resource_entity, resource, resource_space in nearby_resources:
            multiplier = self._get_gather_multiplier(world)
            gathered_amount = min(
                resource.amount,
                self.GATHER_RATE * dt * multiplier
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
        查找附近的指定类型资源（使用空间索引替代全局遍历）
        
        Args:
            world: World实例
            space: 采集者的空间位置
            resource_type: 要采集的资源类型
            radius: 搜索半径
            
        Returns:
            list: [(resource_entity, resource_component, resource_space), ...]
        """
        nearby = []
        from space.space_system import SpaceSystem
        space_system = world.get_system(SpaceSystem)
        
        if space_system is not None:
            ids = space_system.query_radius(
                space.x, space.y, radius, getattr(space, 'layer', 0)
            )
            for eid in ids:
                candidate = world.query_entity(eid)
                if candidate is None:
                    continue
                resource = world.get_component(candidate, ResourceComponent)
                if resource is None or resource.resource_type != resource_type:
                    continue
                res_space = world.get_component(candidate, SpaceComponent)
                if res_space is None:
                    continue
                nearby.append((candidate, resource, res_space))
        
        return nearby

    def _get_gather_multiplier(self, world: World) -> float:
        """读取文明技术带来的采集效率加成"""
        modifier = world.get_world_component(TechnologyModifierComponent)
        if modifier is not None and modifier.gather_multiplier > 0:
            return modifier.gather_multiplier
        return 1.0
