#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:human_death_system.py
@说明:人类死亡判定系统 [已弃用]

⚠️  本文件已弃用。死亡系统已重构为生命周期子领域，新实现位于：
    biology/lifecycle/death/systems/human_death_trigger_system.py
    biology/lifecycle/death/systems/death_system.py
    biology/lifecycle/corpse/systems/corpse_system.py

保留本文件仅用于向后兼容，未来版本将删除。
"""

import logging

from biology.systems.death_system import BaseDeathSystem
from core.world import World

from biology.components.health_status_component import HealthStatusComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.life_cycle_component import LifeCycleComponent

logger = logging.getLogger(__name__)


class HumanDeathSystem(BaseDeathSystem):
    """
    人类死亡判定系统

    处理人类特有的死亡条件判定与执行。
    死亡执行逻辑由 BaseDeathSystem 统一处理。
    """

    def _get_log_prefix(self) -> str:
        return "[HumanDeath]"

    def _collect_dead_entities(self, world: World) -> dict:
        dead_entities: dict = {}

        for entity, (health, needs, age) in world.get_components(
            HealthStatusComponent, PhysiologyNeedsComponent, LifeCycleComponent
        ):
            if age.age >= age.max_age:
                dead_entities[entity] = "old_age"
                continue

            if health.hp <= 0:
                dead_entities[entity] = "hp_depleted"
                continue

            if needs.energy <= 0:
                dead_entities[entity] = "exhaustion"
                continue

            if needs.hunger >= 100:
                dead_entities[entity] = "starvation"
                continue

            if getattr(needs, "thirst", 0) >= 100:
                dead_entities[entity] = "dehydration"
                continue

        return dead_entities