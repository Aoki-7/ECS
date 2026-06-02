#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/death_system.py
@说明:通用生物死亡判定系统 [已弃用]

⚠️  本文件已弃用。死亡系统已重构为生命周期子领域，新实现位于：
    biology/lifecycle/death/systems/death_system.py          (统一执行器)
    biology/lifecycle/death/systems/human_death_trigger_system.py   (人类死亡触发)
    biology/lifecycle/death/systems/creature_death_trigger_system.py (生物死亡触发)
    biology/lifecycle/death/systems/death_event_system.py    (事件传播)
    biology/lifecycle/corpse/systems/corpse_system.py        (尸体处理)

保留本文件仅用于向后兼容，未来版本将删除。
"""

import logging

from core.system import System
from core.world import World
from core.systems.event_log_system import EventLog

from biology.components.energy_component import EnergyComponent
from biology.components.life_cycle_component import LifeCycleComponent

logger = logging.getLogger(__name__)


class BaseDeathSystem(System):
    """
    死亡系统基类（模板方法模式）

    子类只需重写 _collect_dead_entities() 方法，返回 {entity: reason}。
    通用的死亡执行逻辑（日志、EventLog、移除实体）由本基类统一处理。
    """

    tick_interval = 1  # 每1帧执行一次

    def __init__(self):
        super().__init__()
        self.enable_log = True

    def _collect_dead_entities(self, world: World) -> dict:
        """
        收集满足死亡条件的实体。

        子类必须重写此方法，返回 {entity: death_reason} 的字典。
        """
        raise NotImplementedError

    def _get_log_prefix(self) -> str:
        """日志前缀，子类可重写。"""
        return "[Death]"

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        模板方法：检查死亡实体并执行移除。
        """
        dead_entities = self._collect_dead_entities(world)
        prefix = self._get_log_prefix()

        for entity, reason in dead_entities.items():
            if not world.has_entity(entity):
                continue

            entity.metadata["death_reason"] = reason

            if self.enable_log:
                entity_name = getattr(entity, "name", f"E{entity.id}")
                logger.info(f"{prefix} {entity_name}: {reason}")

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
                logger.debug(f"{prefix} 删除实体 {entity.id} 失败: {e}")


class DeathSystem(BaseDeathSystem):
    """
    通用生物死亡判定系统

    处理植物/通用生物的能量耗尽死亡。
    人类特有死亡逻辑由 HumanDeathSystem（继承同一基类）处理。
    """

    def _collect_dead_entities(self, world: World) -> dict:
        dead_entities: dict = {}

        for entity, (energy,) in world.get_components(EnergyComponent):
            # 跳过有 LifeCycleComponent 的实体（如人类），由专门的子系统处理
            if world.get_component(entity, LifeCycleComponent) is not None:
                continue
            if energy.value <= 0:
                dead_entities[entity] = "energy_depleted"

        return dead_entities
