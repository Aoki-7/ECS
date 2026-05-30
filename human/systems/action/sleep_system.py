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

from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.systems.physiological.physiology_needs_system import PhysiologyNeedsHelper
from core.components.action_component import ActionComponent, ActionType, ActionStatus
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent


class SleepSystem(System):
    """
        睡眠系统
        仅负责处理 ActionType.SLEEP 行为。
        恢复疲劳和体力。
    """

    # 睡眠进度速率（约3小时睡够）
    SLEEP_PROGRESS_RATE = 0.5
    # 睡眠期间每小时恢复能量
    SLEEP_ENERGY_RECOVERY = 40.0
    # 睡眠期间每小时减少疲劳
    SLEEP_FATIGUE_RECOVERY = 30.0
    # 睡眠完成额外恢复能量
    SLEEP_FINISH_ENERGY_BONUS = 30.0
    # 睡眠完成额外减少疲劳
    SLEEP_FINISH_FATIGUE_BONUS = 10.0
    # 睡眠完成减少口渴
    SLEEP_FINISH_THIRST_REDUCTION = 10.0
    # 睡眠完成减少饥饿
    SLEEP_FINISH_HUNGER_REDUCTION = 5.0

    def update(self, world: World, dt: float):
        for entity, (needs, action, task) in world.get_components(
            PhysiologyNeedsComponent, ActionComponent, TaskComponent
        ):
            needs: PhysiologyNeedsComponent
            action: ActionComponent
            task: TaskComponent

            if action.current_action != ActionType.SLEEP:
                continue

            # 模拟睡眠过程（约3小时睡够）
            action.progress += dt * self.SLEEP_PROGRESS_RATE

            # 睡眠期间逐步恢复能量（避免在睡完前能量耗尽死亡）
            PhysiologyNeedsHelper.add_energy(needs, self.SLEEP_ENERGY_RECOVERY * dt)
            PhysiologyNeedsHelper.add_fatigue(needs, -self.SLEEP_FATIGUE_RECOVERY * dt)

            if action.progress >= 1.0:
                # 睡眠完成额外恢复
                PhysiologyNeedsHelper.add_energy(needs, self.SLEEP_FINISH_ENERGY_BONUS)
                PhysiologyNeedsHelper.add_fatigue(needs, -self.SLEEP_FINISH_FATIGUE_BONUS)
                PhysiologyNeedsHelper.add_thirst(needs, -self.SLEEP_FINISH_THIRST_REDUCTION)
                PhysiologyNeedsHelper.add_hunger(needs, -self.SLEEP_FINISH_HUNGER_REDUCTION)

                # 记录到记忆
                memory = world.get_component(entity, MemoryComponent)
                space = world.get_component(entity, SpaceComponent)
                current_time = world.get_time().total_hours
                if memory:
                    memory.add_event(
                        current_time, "slept",
                        f"在 ({space.x if space else '?'}, {space.y if space else '?'}) 休息恢复体力",
                        impact=0.4,
                        location=(space.x, space.y) if space else None
                    )
                    memory.record_success("rest")

                # 标记完成
                action.progress = 1.0
                action.status = ActionStatus.SUCCESS
                task.status = TaskStatus.DONE