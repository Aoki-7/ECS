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

from biology.components.energy_component import (
    EnergyComponent,
)

from human.components.physiological.health_component import (
    HealthComponent,
)

from human.components.physiological.physiology_needs_component import (
    PhysiologyNeedsComponent,
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
        """

        dead_entities = {}

        # =====================================================
        # 1. HealthComponent
        # =====================================================

        for entity, components in world.get_components(
            HealthComponent
        ):
            health = components[0]

            if health.hp <= 0:
                dead_entities[entity] = "hp_depleted"

        # =====================================================
        # 2. PhysiologyNeedsComponent
        # =====================================================

        for entity, components in world.get_components(
            PhysiologyNeedsComponent
        ):
            needs = components[0]

            # 体力耗尽
            if needs.energy <= 0:
                dead_entities[entity] = "exhaustion"

            # 饥饿致死
            elif needs.hunger >= 100:
                dead_entities[entity] = "starvation"

            # 极端脱水
            elif hasattr(needs, "thirst"):
                if needs.thirst >= 100:
                    dead_entities[entity] = "dehydration"

        # =====================================================
        # 3. 生物 EnergyComponent
        # =====================================================

        for entity, components in world.get_components(
            EnergyComponent
        ):
            energy = components[0]

            if energy.value <= 0:
                dead_entities[entity] = "energy_depleted"

        # =====================================================
        # 4. 执行死亡
        # =====================================================

        removed_count = 0

        for entity, reason in dead_entities.items():

            if not world.has_entity(entity):
                continue

            # 可选：标记死亡原因
            if hasattr(entity, "death_reason"):
                entity.death_reason = reason

            # Debug 日志
            if self.enable_log:
                entity_name = getattr(
                    entity,
                    "name",
                    f"Entity<{entity.id}>"
                )

                print(
                    f"[DeathSystem] "
                    f"{entity_name} died: {reason}"
                )

            try:
                world.remove_entity(entity)
                removed_count += 1

            except Exception as e:
                print(
                    f"[DeathSystem] "
                    f"remove_entity failed: {e}"
                )

        # =====================================================
        # 5. Summary
        # =====================================================

        if removed_count > 0 and self.enable_log:
            print(
                f"[DeathSystem] "
                f"removed {removed_count} dead entities"
            )