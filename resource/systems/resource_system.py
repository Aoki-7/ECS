#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:resource_system.py
@说明:资源管理系统

职责：
    - 消耗资源（consume）
    - 添加资源（add）
    - 资源再生（regenerate）
    - 锁定/解锁资源
    - 元数据管理
'''

import logging
from typing import Optional, Any

from core.system import System
from core.world import World
from core.entity import Entity

from resource.components.resource_component import ResourceComponent, ResourceState

logger = logging.getLogger(__name__)


class ResourceSystem(System):
    """资源管理系统"""

    tick_interval = 1  # 每帧执行（资源再生）

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行资源再生"""
        for entity, (resource,) in world.get_components(ResourceComponent):
            if resource.regenerable and resource.state != ResourceState.LOCKED:
                self.regenerate(entity, resource, dt)

    def consume(self, entity: Entity, resource: ResourceComponent, amount: float) -> float:
        """
        消耗资源
        
        参数:
            entity: 实体
            resource: 资源组件
            amount: 尝试消耗的数量
            
        返回:
            实际消耗的数量
        """
        if resource.state == ResourceState.LOCKED or resource.state == ResourceState.DEPLETED:
            return 0.0
            
        actual_amount = min(amount, resource.amount)
        resource.amount -= actual_amount
        self._sync_state(resource)
        
        logger.debug(f"[Resource] 实体 {entity.id} 消耗 {actual_amount} {resource.resource_type}")
        return actual_amount

    def add(self, entity: Entity, resource: ResourceComponent, amount: float) -> float:
        """
        添加资源
        
        参数:
            entity: 实体
            resource: 资源组件
            amount: 尝试添加的数量
            
        返回:
            实际添加的数量
        """
        if resource.state == ResourceState.LOCKED:
            return 0.0
            
        actual_amount = min(amount, resource.max_amount - resource.amount)
        resource.amount += actual_amount
        self._sync_state(resource)
        
        logger.debug(f"[Resource] 实体 {entity.id} 添加 {actual_amount} {resource.resource_type}")
        return actual_amount

    def regenerate(self, entity: Entity, resource: ResourceComponent, delta_time: float = 1.0) -> None:
        """
        资源再生
        
        参数:
            entity: 实体
            resource: 资源组件
            delta_time: 时间增量
        """
        if not resource.regenerable or resource.state == ResourceState.LOCKED:
            return
            
        regen_amount = resource.regen_rate * delta_time
        self.add(entity, resource, regen_amount)

    def lock(self, resource: ResourceComponent) -> None:
        """锁定资源"""
        resource.state = ResourceState.LOCKED

    def unlock(self, resource: ResourceComponent) -> None:
        """解锁资源"""
        self._sync_state(resource)

    def is_available(self, resource: ResourceComponent) -> bool:
        """检查资源是否可用"""
        return resource.state == ResourceState.AVAILABLE

    def get_metadata(self, resource: ResourceComponent, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return resource.metadata.get(key, default)

    def set_metadata(self, resource: ResourceComponent, key: str, value: Any) -> None:
        """设置元数据"""
        resource.metadata[key] = value

    def _sync_state(self, resource: ResourceComponent) -> None:
        """根据当前数量同步资源状态"""
        if resource.state == ResourceState.LOCKED:
            return
        if resource.amount <= 0:
            resource.state = ResourceState.DEPLETED
        elif resource.amount < resource.max_amount and resource.regenerable:
            resource.state = ResourceState.REGENERATING
        else:
            resource.state = ResourceState.AVAILABLE
