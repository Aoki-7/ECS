#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ActionManagementSystem — v4.0 新增

职责：
    - 管理 ActionComponent 的所有业务逻辑
    - 动作重置、队列管理等

设计原则：
    - Component 纯数据，System 处理逻辑
    - 静态工具方法供其他 System 调用
"""

from core.system import System
from core.world import World

from human.components.action.action_component import ActionComponent, ActionType, ActionStatus


class ActionManagementSystem(System):
    """动作管理系统"""

    tick_interval = 1

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)
        # 动作队列调度：空闲时自动执行队列中的下一个动作
        for entity, action in world.get_components(ActionComponent):
            if action.status in (ActionStatus.IDLE, ActionStatus.SUCCESS,
                                 ActionStatus.FAILED, ActionStatus.INTERRUPTED):
                if action.action_queue:
                    action.current_action = action.action_queue.pop(0)
                    action.status = ActionStatus.RUNNING
                    action.progress = 0.0

    @staticmethod
    def reset(action: ActionComponent):
        """重置当前动作"""
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.IDLE
        action.progress = 0.0
        action.target_entity = None
        action.target_pos = None
        action._path = []
        action._path_index = 0

    @staticmethod
    def queue_action(action: ActionComponent, action_type: ActionType):
        """将动作加入队列"""
        action.action_queue.append(action_type)

    @staticmethod
    def dequeue_action(action: ActionComponent) -> ActionType:
        """从队列取出下一个动作"""
        if action.action_queue:
            return action.action_queue.pop(0)
        return ActionType.IDLE

    @staticmethod
    def clear_queue(action: ActionComponent):
        """清空动作队列"""
        action.action_queue.clear()

    @staticmethod
    def is_idle(action: ActionComponent) -> bool:
        """检查是否空闲"""
        return action.current_action == ActionType.IDLE

    @staticmethod
    def is_running(action: ActionComponent) -> bool:
        """检查是否正在执行"""
        return action.status == ActionStatus.RUNNING
