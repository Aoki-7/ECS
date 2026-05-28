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
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent


class SleepSystem(System):
    """
        睡眠系统
        仅负责处理 ActionType.SLEEP 行为。
        恢复疲劳和体力。
    """

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
            action.progress += dt * 0.5

            # 睡眠期间逐步恢复能量（避免在睡完前能量耗尽死亡）
            needs.add_energy(40 * dt)  # 每小时恢复40能量
            needs.add_fatigue(-30 * dt)  # 每小时减少30疲劳

            if action.progress >= 1.0:
                # 睡眠完成额外恢复
                needs.add_energy(30)  # 额外恢复
                needs.add_fatigue(-10)  # 额外减少疲劳
                needs.add_thirst(-10)  # 睡眠中减少口渴
                needs.add_hunger(-5)   # 睡眠中减少饥饿

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