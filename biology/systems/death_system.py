#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/death_system.py
@说明:通用生物死亡判定系统

负责检测并移除满足死亡条件的通用生物实体。

死亡条件：
    - energy.value <= 0  → 能量耗尽
"""

import logging

from core.system import System
from core.world import World
from core.systems.event_log_system import EventLog

from biology.components.energy_component import EnergyComponent
from biology.components.life_cycle_component import LifeCycleComponent

logger = logging.getLogger(__name__)


class DeathSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    通用生物死亡判定系统

    处理植物/通用生物的能量耗尽死亡。
    人类特有死亡逻辑已迁移至 human/systems/physiological/human_death_system.py
    """

    def __init__(self):
        super().__init__()
        self.enable_log = True

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        检查死亡实体并移除
        """
        dead_entities: dict = {}

        for entity, (energy,) in world.get_components(EnergyComponent):
            # 跳过人类实体（由 HumanDeathSystem 处理，避免竞态删除）
            if world.get_component(entity, LifeCycleComponent) is not None:
                continue
            if energy.value <= 0:
                dead_entities[entity] = "energy_depleted"

        for entity, reason in dead_entities.items():
            if not world.has_entity(entity):
                continue

            if hasattr(entity, "death_reason"):
                entity.death_reason = reason

            if self.enable_log:
                entity_name = getattr(entity, "name", f"E{entity.id}")
                logger.info(f"[Death] {entity_name}: {reason}")

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
                # 实体可能已被其他系统移除
                logger.debug(f"[Death] 删除实体 {entity.id} 失败: {e}")
