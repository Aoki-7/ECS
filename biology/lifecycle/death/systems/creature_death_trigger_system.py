#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
CreatureDeathTriggerSystem — 通用生物死亡触发系统

职责：
    检测非人类生物（植物、动物等）的能量耗尽，挂载 PendingDeathComponent。
    不直接删除实体 —— 死亡执行由 DeathSystem 统一处理。

排除范围：
    - 有 LifeCycleComponent 的实体（人类），由 HumanDeathTriggerSystem 处理
"""

import logging

from core.system import System
from core.world import World

from biology.lifecycle.components.energy_component import EnergyComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.lifecycle.death.components.pending_death_component import PendingDeathComponent

logger = logging.getLogger(__name__)


class CreatureDeathTriggerSystem(System):
    tick_interval = 1

    def update(self, world: World, dt: float = 1.0) -> None:
        time_component = world.get_time()
        world_time = time_component.total_hours if time_component else 0.0

        for entity, (energy,) in world.get_components(EnergyComponent):
            if not world.has_entity(entity):
                continue

            # 跳过有 LifeCycleComponent 的实体（人类），由专门的触发系统处理
            if world.get_component(entity, LifeCycleComponent) is not None:
                continue

            # 如果已经标记死亡，跳过
            if world.get_component(entity, PendingDeathComponent) is not None:
                continue

            if energy.value <= 0:
                world.add_component(entity, PendingDeathComponent(
                    reason="energy_depleted",
                    source_system="CreatureDeathTriggerSystem",
                    priority=5,
                    timestamp=world_time,
                    details=f"energy={energy.value:.1f}"
                ))
