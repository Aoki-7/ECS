#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:socialize_system.py
@说明:社交系统
@时间:2026/04/14
@作者:GitHub Copilot
@版本:1.0
'''

from core.system import System
from core.world import World

from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus


class SocializeSystem(System):
    """
    社交系统
    处理社交行为，增加社会需求满足。
    """

    def update(self, world: World, dt: float):
        for _, (needs, action, task) in world.get_components(
            PhysiologyNeedsComponent, ActionComponent, TaskComponent
        ):
            needs: PhysiologyNeedsComponent
            action: ActionComponent
            task: TaskComponent

            if action.current_action != ActionType.SOCIALIZE:
                continue

            # 模拟社交过程
            action.progress += dt * 0.2  # 5秒社交完成

            if action.progress >= 1.0:
                # 社交完成，增加社会满足
                needs.add_social(30)

                # 标记完成，由 ActionSystem 处理
                action.progress = 1.0
                task.status = TaskStatus.DONE