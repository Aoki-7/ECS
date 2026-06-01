#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:human_death_system.py
@说明:人类死亡判定系统

负责检测并移除满足死亡条件的人类实体。

死亡条件：
    - hp <= 0           → 生命值耗尽
    - energy <= 0       → 能量耗尽
    - hunger >= 100     → 饥饿致死
    - thirst >= 100     → 脱水致死
    - age >= max_age    → 老死
"""

import logging

from core.system import System
from core.world import World
from core.systems.event_log_system import EventLog

from biology.components.health_status_component import HealthStatusComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.life_cycle_component import LifeCycleComponent

logger = logging.getLogger(__name__)


class HumanDeathSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    人类死亡判定系统

    处理人类特有的死亡条件判定与执行。
    """

    def __init__(self):
        super().__init__()
        self.enable_log = True

    def update(self, world: World, dt: float = 1.0):
        """
        检查人类死亡实体并移除
        """
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

        # 执行死亡
        for entity, reason in dead_entities.items():
            if not world.has_entity(entity):
                continue

            if hasattr(entity, "death_reason"):
                entity.death_reason = reason

            if self.enable_log:
                entity_name = getattr(entity, "name", f"E{entity.id}")
                logger.info(f"[HumanDeath] {entity_name}: {reason}")

                EventLog.log(
                    world,
                    event_type="death",
                    description=f"{entity_name} 死亡，原因: {reason}",
                    entity_id=entity.id,
                    data={"reason": reason, "entity_name": entity_name},
                    severity="critical"
                )

            try:
                world.remove_entity(entity)
            except Exception as e:
                logger.warning(f"[HumanDeath] 删除实体 {entity.id} 失败: {e}")