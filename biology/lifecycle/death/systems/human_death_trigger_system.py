#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
HumanDeathTriggerSystem — 人类死亡触发系统

职责：
    检测人类是否满足死亡条件，若满足则挂载 PendingDeathComponent。
    不直接删除实体 —— 死亡执行由 DeathSystem 统一处理。

死亡条件：
    - hp <= 0           → hp_depleted
    - energy <= 0       → exhaustion
    - hunger >= 100     → starvation
    - thirst >= 100     → dehydration
    - age >= max_age    → old_age
"""

import logging

from core.system import System
from core.world import World

from biology.components.health_status_component import HealthStatusComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.lifecycle.death.components.pending_death_component import PendingDeathComponent

logger = logging.getLogger(__name__)


class HumanDeathTriggerSystem(System):
    tick_interval = 1

    # 饥饿/口渴死亡优先级略高，因为它们是直接生存需求
    DEATH_PRIORITIES = {
        "starvation": 10,
        "dehydration": 10,
        "hp_depleted": 8,
        "exhaustion": 5,
        "old_age": 3,
    }

    def update(self, world: World, dt: float = 1.0) -> None:
        time_component = world.get_time()
        world_time = time_component.total_hours if time_component else 0.0

        for entity, (health, needs, age) in world.get_components(
            HealthStatusComponent, PhysiologyNeedsComponent, LifeCycleComponent
        ):
            if not world.has_entity(entity):
                continue

            # 如果已经标记死亡，跳过
            if world.get_component(entity, PendingDeathComponent) is not None:
                continue

            reason = None
            details = ""

            if age.current_age >= age.max_age:
                reason = "old_age"
                details = f"age={age.current_age:.0f}/{age.max_age:.0f}"
            elif health.hp <= 0:
                reason = "hp_depleted"
                details = f"hp={health.hp:.1f}"
            elif needs.energy <= 0:
                reason = "exhaustion"
                details = f"energy={needs.energy:.1f}"
            elif needs.hunger >= 100:
                reason = "starvation"
                details = f"hunger={needs.hunger:.1f}"
            elif getattr(needs, "thirst", 0) >= 100:
                reason = "dehydration"
                details = f"thirst={needs.thirst:.1f}"

            if reason is not None:
                priority = self.DEATH_PRIORITIES.get(reason, 0)
                world.add_component(entity, PendingDeathComponent(
                    reason=reason,
                    source_system="HumanDeathTriggerSystem",
                    priority=priority,
                    timestamp=world_time,
                    details=details
                ))