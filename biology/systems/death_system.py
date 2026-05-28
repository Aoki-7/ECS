#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@文件:death_system.py
@说明:统一死亡系统
@时间:2026/03/18
@作者:Sherry
@版本:2.0
"""

from core.system import System
from core.world import World
from core.event_log_component import EventLog

from biology.components.energy_component import (
    EnergyComponent,
)

from human.components.physiological.health_component import (
    HealthComponent,
)

from human.components.physiological.physiology_needs_component import (
    PhysiologyNeedsComponent,
)

from human.components.basic.age_component import (
    AgeComponent,
)


class DeathSystem(System):
    """
    统一死亡判定系统

    死亡条件：
    1. hp <= 0
    2. energy <= 0
    3. hunger >= 100
    4. biological energy <= 0
    """

    def __init__(self):
        super().__init__()

        self.enable_log = True

    # =========================================================
    # ECS Update
    # =========================================================

    def update(self, world: World, dt: float = 1.0):
        """
        检查死亡实体并移除
        合并为单次遍历，减少重复查询开销
        """

        dead_entities = {}

        # =====================================================
        # 单次遍历：同时查询 Health + PhysiologyNeeds + Energy
        # 优先使用三元组查询，若某个组件缺失则跳过对应检查
        # =====================================================

        # 策略：遍历所有有 HealthComponent 或 PhysiologyNeedsComponent 或 EnergyComponent 的实体
        # 由于 get_components 要求所有组件都存在，我们改用三次遍历但只遍历一次主循环
        # 实际上，对于大部分实体（人类）三者都有；植物有 EnergyComponent
        # 最优方案：遍历 HealthComponent+PhysiologyNeedsComponent（人类），再遍历 EnergyComponent（植物）

        # Pass A: 人类（同时有 Health + PhysiologyNeeds + Age）
        for entity, (health, needs, age) in world.get_components(HealthComponent, PhysiologyNeedsComponent, AgeComponent):
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

        # Pass B: 植物/生物（EnergyComponent，且不在 Pass A 中已判定死亡）
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
                    world, event_type="death",
                    description=f"{entity_name} 死亡，原因: {reason}",
                    entity_id=entity.id,
                    data={"reason": reason, "entity_name": entity_name},
                    severity="critical"
                )

            try:
                world.remove_entity(entity)
                removed_count += 1
            except Exception:
                pass