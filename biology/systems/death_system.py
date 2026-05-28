#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/death_system.py
@说明:统一死亡判定系统

负责检测并移除满足死亡条件的实体。

死亡条件（通用层）：
    - energy.value <= 0  → 能量耗尽

死亡条件（人类特有层，见下方 TODO）：
    - hp <= 0
    - energy <= 0
    - hunger >= 100
    - thirst >= 100
    - age >= max_age

TODO(架构): 当前 DeathSystem 直接依赖 human 模块的组件（HealthComponent、
PhysiologyNeedsComponent、AgeComponent），造成跨层耦合。
biology 作为基础层不应知晓上层 human 的存在。
建议未来拆分为：
    - biology/systems/energy_death_system.py  — 仅处理 EnergyComponent
    - human/systems/human_death_system.py     — 处理人类特有死亡条件
"""

from core.system import System
from core.world import World
from core.event_log_component import EventLog

from biology.components.energy_component import EnergyComponent

# TODO: 以下导入造成跨层耦合，应迁移至 human 模块的独立系统
from human.components.physiological.health_component import HealthComponent
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.basic.age_component import AgeComponent


class DeathSystem(System):
    """
    统一死亡判定系统

    采用两阶段遍历策略：
        Pass A: 人类实体（Health + PhysiologyNeeds + Age）
        Pass B: 通用生物实体（EnergyComponent，排除已在 Pass A 中判定死亡的）

    最后统一执行移除并记录死亡日志。
    """

    def __init__(self):
        super().__init__()
        self.enable_log = True

    def update(self, world: World, dt: float = 1.0):
        """
        检查死亡实体并移除

        合并为单次遍历逻辑（两阶段），减少重复查询开销。
        """
        dead_entities: dict = {}

        # =====================================================
        # Pass A: 人类（同时有 Health + PhysiologyNeeds + Age）
        # TODO: 迁移至 human 模块的 HumanDeathSystem
        # =====================================================
        for entity, (health, needs, age) in world.get_components(
            HealthComponent, PhysiologyNeedsComponent, AgeComponent
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

        # =====================================================
        # Pass B: 植物/通用生物（EnergyComponent）
        # 跳过已在 Pass A 中判定死亡的实体
        # =====================================================
        for entity, (energy,) in world.get_components(EnergyComponent):
            if entity in dead_entities:
                continue
            if energy.value <= 0:
                dead_entities[entity] = "energy_depleted"

        # =====================================================
        # 执行死亡
        # =====================================================
        removed_count = 0

        for entity, reason in dead_entities.items():
            if not world.has_entity(entity):
                continue

            # 可选：标记死亡原因
            if hasattr(entity, "death_reason"):
                entity.death_reason = reason

            if self.enable_log:
                entity_name = getattr(entity, "name", f"E{entity.id}")
                print(f"[Death] {entity_name}: {reason}")

                # 记录到全局事件日志
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
                removed_count += 1
            except Exception:
                # 实体可能已被其他系统移除
                pass
