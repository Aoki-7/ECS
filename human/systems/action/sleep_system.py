#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:sleep_system.py
@说明:睡眠系统
@时间:2026/04/13
@作者:GitHub Copilot
@版本:1.0
'''

from core.system import System
from core.world import World

from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus


class SleepSystem(System):
    """
        睡眠系统
        仅负责处理 ActionType.SLEEP 行为。
        恢复疲劳和体力。
    """

    def update(self, world: World, dt: float):
        for _, (needs, action, task) in world.get_components(
            PhysiologyNeedsComponent, ActionComponent, TaskComponent
        ):
            needs: PhysiologyNeedsComponent
            action: ActionComponent
            task: TaskComponent

            if action.current_action != ActionType.SLEEP:
                continue

            # 模拟睡眠过程（约3小时睡够）
            action.progress += dt * 0.3

            if action.progress >= 1.0:
                # 睡眠完成：完全恢复能量和体力
                needs.add_fatigue(-100)  # 减少疲劳
                needs.add_energy(100)  # 完全恢复能量

                # 标记完成，由 ActionSystem 处理
                action.progress = 1.0
                task.status = TaskStatus.DONE