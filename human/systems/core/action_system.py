#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:action_system.py
@说明:
@时间:2026/04/01 15:41:59
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World

from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent


class ActionSystem(System):
    """
        动作总控系统（调度器）
        
        负责：
        - 管理动作队列
        - 调度当前动作
        - 检查动作完成状态
        - 切换到下一个动作
        
        不执行具体动作逻辑，由专用子系统（如 EatSystem, DrinkSystem 等）处理。
    """
    def update(self, world: World, dt):
        for _, (action, needs) in world.get_components(ActionComponent, PhysiologyNeedsComponent):
            
            if action is None or needs is None:
                continue

            action: ActionComponent
            needs: PhysiologyNeedsComponent
            
            # 没任务且当前空闲
            if not action.action_queue and action.current_action == ActionType.IDLE:
                continue

            # 取下一个动作
            if action.current_action == ActionType.IDLE and action.action_queue:
                action.current_action = action.action_queue.pop(0)
                action.progress = 0.0
                action.status = ActionStatus.RUNNING

            # 检查当前动作是否完成（由子系统更新 progress 或 status）
            if action.current_action != ActionType.IDLE:
                if action.progress >= 1.0 or action.status in [ActionStatus.SUCCESS, ActionStatus.FAILED]:
                    # 动作完成或失败，重置状态
                    action.current_action = ActionType.IDLE
                    if action.status != ActionStatus.FAILED:
                        action.status = ActionStatus.SUCCESS
                    action.progress = 0.0
                    
                    # 如果队列还有动作，继续调度
                    if action.action_queue:
                        action.current_action = action.action_queue.pop(0)
                        action.progress = 0.0
                        action.status = ActionStatus.RUNNING
