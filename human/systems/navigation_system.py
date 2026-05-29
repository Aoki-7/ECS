#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""导航系统 - 自动寻路和移动决策"""

from core.system import System
from core.world import World
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple, Optional, Dict
import math
import random

from biology.components.body_component import BodyComponent
from core.components.velocity_component import VelocityComponent
from core.components.action_component import ActionComponent, ActionType, ActionStatus
from space.space_component import SpaceComponent


@dataclass
class NavigationSystem(System):
    """导航系统 - 负责自动寻路和移动决策
    
    【功能】
    - 自动规划路径（简单 A*算法简化版本）
    - 避障移动
    - 转向目标点移动
    - 随机探索移动
    """

    def update(self, world: World, dt):
        """每帧更新导航状态"""
        for entity, (action,) in world.get_components(ActionComponent):
            if action is None:
                continue
            
            action: ActionComponent
            
            # 检查当前动作是否需要移动
            if action.current_action == ActionType.MOVE_TO and action.target_pos:
                self._move_to_target(world, entity, action, dt)
            
            elif action.current_action == ActionType.MOVE_RANDOM:
                self._random_move(world, entity, action, dt)
            
            elif action.current_action in [ActionType.SEARCH, ActionType.EXPLORE]:
                self._search_explore(world, entity, action, dt)

    def _move_to_target(self, world: World, entity, action: ActionComponent, dt: float):
        """移动到目标点
        
        Args:
            action: 当前动作组件
        """
        if not action.target_pos or action.progress >= 1.0:
            return
        
        if not hasattr(action, 'start_pos') or action.start_pos is None:
            return
        
        # 计算到目标的距离
        start = action.start_pos
        target = action.target_pos
        
        if start is None:
            start = (0, 0, 0)
        
        # 简单直线移动（忽略障碍物）
        dx = target[0] - start[0]
        dy = target[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # 更新进度
        action.progress = min(1.0, action.progress + dt * 2.0)  # 移动速度
        
        # 更新当前位置
        new_x = start[0] + dx * action.progress
        new_y = start[1] + dy * action.progress
        new_z = start[2] if len(start) > 2 else 0
        
        # 更新实体的位置（通过 SpaceComponent）
        sc = world.get_component(entity, SpaceComponent)
        if sc and hasattr(sc, 'x') and hasattr(sc, 'y'):
            sc.x = new_x
            sc.y = new_y
            if hasattr(sc, 'z'):
                sc.z = new_z

    def _random_move(self, world: World, entity, action: ActionComponent, dt: float):
        """随机移动
        
        Args:
            action: 当前动作组件
        """
        # 生成随机方向
        angle = random.random() * 2 * math.pi
        speed = 0.5  # 移动速度
        
        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed
        dz = 0
        
        # 更新位置
        sc = world.get_component(entity, SpaceComponent)
        if sc and hasattr(sc, 'x') and hasattr(sc, 'y'):
            sc.x += dx
            sc.y += dy
            if hasattr(sc, 'z'):
                sc.z += dz

    def _search_explore(self, world: World, entity, action: ActionComponent, dt: float):
        """搜索/探索行为
        
        Args:
            action: 当前动作组件
        """
        # 随机选择探索方向，但避免返回安全区
        angle = random.random() * 2 * math.pi
        speed = 0.8  # 探索移动速度
        
        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed
        
        # 更新位置
        sc = world.get_component(entity, SpaceComponent)
        if sc and hasattr(sc, 'x') and hasattr(sc, 'y'):
            sc.x += dx
            sc.y += dy

    def calculate_path(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """简单的路径规划（A*算法简化版）
        
        由于我们只有简单世界，使用直线路径。
        如果有障碍物信息，可以使用更复杂的路径规划。
        
        Args:
            start: 起点坐标 (x, y)
            end: 终点坐标 (x, y)
            
        Returns:
            路径点列表
        """
        # 简化为直线路径
        path = []
        distance = math.sqrt(
            (end[0] - start[0])**2 + 
            (end[1] - start[1])**2
        )
        
        if distance == 0:
            return [(start[0], start[1])]
        
        # 生成路径点
        num_points = max(5, int(distance * 10))
        for i in range(num_points + 1):
            t = i / num_points
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t
            path.append((x, y))
        
        return path

    def find_nearest_resource(self, entity_pos: Tuple[float, float], 
                               resource_types: List[str]) -> Optional[Tuple[float, float, str]]:
        """寻找最近的资源
        
        Args:
            entity_pos: 实体当前位置 (x, y)
            resource_types: 要查找的资源类型列表
            
        Returns:
            最近资源的坐标和类型，或 None
        """
        nearest = None
        nearest_dist = float('inf')
        
        for _, (resource,) in world.get_components(ResourceComponent):
            if not resource or resource.resource_type not in resource_types:
                continue
            
            dist = math.sqrt(
                (resource.x - entity_pos[0])**2 + 
                (resource.y - entity_pos[1])**2
            )
            
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = (resource.x, resource.y, resource.resource_type)
        
        return nearest

    def is_safe(self, pos: Tuple[float, float]) -> bool:
        """检查位置是否安全（远离危险区域）
        
        Args:
            pos: 要检查的位置
            
        Returns:
            是否安全
        """
        for _, (danger,) in world.get_components(DangerComponent):
            if not danger:
                continue
            
            dist = math.sqrt(
                (danger.x - pos[0])**2 + 
                (danger.y - pos[1])**2
            )
            
            if dist < 50.0:  # 危险区域半径
                return False
        
        return True


# 行为决策优先级映射
ACTION_PRIORITY = {
    'eat': 0.9,
    'drink': 0.8,
    'sleep': 0.7,
    'return': 0.6,
    'explore': 0.3,
    'search': 0.5,
}


# 行为决策函数
def behavior_decision(
    needs: Dict[str, float], 
    current_action: ActionType,
    nearest_resource: Optional[Tuple[float, float, str]] = None,
    danger_level: float = 0.0
) -> ActionType:
    """根据需求状态和行为决策生成动作
    
    Args:
        needs: 当前需求字典 {'food': 50.0, 'water': 20.0, ...}
        current_action: 当前执行的动作
        nearest_resource: 最近的资源位置
        danger_level: 危险级别
        
    Returns:
        新的动作类型
    """
    decision = current_action
    
    # 检查是否有更紧急的需求
    if needs.get('food', 0) < 20.0:
        return ActionType.EAT
    elif needs.get('water', 0) < 20.0:
        return ActionType.DRINK
    elif needs.get('sleep', 100) < 30.0:
        return ActionType.SLEEP
    
    # 检查危险情况
    if danger_level > 0.8:
        return ActionType.FLEE
    
    # 检查资源可用性
    if nearest_resource:
        if nearest_resource[2] == 'food' and needs.get('food', 100) < 50:
            return ActionType.PICKUP
        elif nearest_resource[2] == 'water' and needs.get('water', 100) < 50:
            return ActionType.DRINK
    
    # 正常探索行为
    if current_action == ActionType.IDLE or decision == ActionType.WAIT:
        # 返回安全区
        return ActionType.RETURN
        
    return decision


# 简单的资源数据结构（如需要，可在系统中补充）
@dataclass
class ResourceComponent:
    """资源组件"""
    resource_type: str = "food"
    quantity: float = 10.0
    x: float = 0.0
    y: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "resource_type": self.resource_type,
            "quantity": self.quantity,
            "x": self.x,
            "y": self.y
        }


# 危险区域组件（用于安全检查）
@dataclass
class DangerComponent:
    """危险区域组件"""
    x: float = 0.0
    y: float = 0.0
    danger_level: float = 1.0