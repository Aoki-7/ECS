#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:planning_decision_maker.py
@说明:规划决策器

职责：
    - 判断当前状态是否允许规划
    - 中断当前动作
'''

from human.components.action.action_component import ActionComponent, ActionType, ActionStatus


class PlanningDecisionMaker:
    """规划决策器"""

    def should_plan(self, action: ActionComponent, is_critical: bool, needs) -> bool:
        """判断当前状态是否允许规划"""
        # 非危险状态下，执行具体动作时不规划
        if not is_critical and action.current_action not in (
            ActionType.IDLE, ActionType.MOVE_TO, ActionType.EXPLORE
        ):
            return False
        
        # 危险状态下强制中断并重新规划
        if is_critical:
            self.interrupt_action(action)
            return True
        
        # 中断移动以便新规划
        if action.current_action == ActionType.MOVE_TO:
            self.interrupt_action(action)
            return True
        
        # 探索状态下允许规划（避免EXPLORE错误）
        if action.current_action == ActionType.EXPLORE:
            return True
        
        # 睡眠中检查是否需中断
        if action.current_action == ActionType.SLEEP:
            if needs and (needs.hunger > 85 or needs.thirst > 85):
                self.interrupt_action(action)
                return True
            return False
        
        return True

    def interrupt_action(self, action: ActionComponent) -> None:
        """中断当前动作"""
        action.current_action = ActionType.IDLE
        action.status = ActionStatus.IDLE
        action.progress = 0.0