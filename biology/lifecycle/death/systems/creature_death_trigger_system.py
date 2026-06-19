#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
CreatureDeathTriggerSystem — 通用生物死亡触发系统

职责：
    检测非人类生物（植物、动物等）的能量耗尽或衰老，挂载 PendingDeathComponent。
    不直接删除实体 —— 死亡执行由 DeathSystem 统一处理。

排除范围：
    - 有人类组件的实体，由 HumanDeathTriggerSystem 处理
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

            # 跳过人类实体，由 HumanDeathTriggerSystem 处理
            try:
                from human.components.basic.human_component import HumanComponent
                if world.get_component(entity, HumanComponent) is not None:
                    continue
            except ImportError:
                logger.warning("HumanComponent not available, skipping human check")

            # 如果已经标记死亡，跳过
            if world.get_component(entity, PendingDeathComponent) is not None:
                continue

            # 条件 1：能量耗尽
            if energy.value <= 0:
                world.add_component(entity, PendingDeathComponent(
                    reason="energy_depleted",
                    source_system="CreatureDeathTriggerSystem",
                    priority=5,
                    timestamp=world_time,
                    details=f"energy={energy.value:.1f}"
                ))
                continue

            # 条件 2：衰老（年龄超过最大寿命）
            lifecycle = world.get_component(entity, LifeCycleComponent)
            if lifecycle is not None:
                if lifecycle.current_age >= lifecycle.max_age:
                    world.add_component(entity, PendingDeathComponent(
                        reason="old_age",
                        source_system="CreatureDeathTriggerSystem",
                        priority=3,
                        timestamp=world_time,
                        details=f"age={lifecycle.current_age:.1f}, max_age={lifecycle.max_age:.1f}"
                    ))
                    continue
