#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
死亡系统（统一版）

处理以下死亡条件：
1. HealthComponent.hp <= 0 → 生命值归零
2. PhysiologyNeedsComponent.energy <= 0 → 体力耗尽
3. PhysiologyNeedsComponent.hunger >= 100 → 饥饿致死
4. EnergyComponent.value <= 0 → 植物等生物能量耗尽
"""

from core.system import System
from core.world import World
from biology.components.energy_component import EnergyComponent
from human.components.physiological.health_component import HealthComponent
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent


class DeathSystem(System):
    """
    统一死亡判定系统
    检查所有实体的生存状态，将应死亡的实体从世界中移除。
    """

    def _update(self, world: World, dt: float = 1.0):
        dead = set()

        # 1. 检查 HealthComponent（hp <= 0）
        for entity, [health] in world.get_components(HealthComponent):
            if health.hp <= 0:
                dead.add(entity)

        # 2. 检查 PhysiologyNeedsComponent（体力耗尽 or 饥饿致死）
        for entity, [needs] in world.get_components(PhysiologyNeedsComponent):
            if needs.energy <= 0 or needs.hunger >= 100:
                dead.add(entity)

        # 3. 检查 EnergyComponent（植物等生物能量耗尽）
        for entity, [energy] in world.get_components(EnergyComponent):
            if energy.value <= 0:
                dead.add(entity)

        # 移除所有已死亡实体
        for e in dead:
            if world.has_entity(e):
                world.remove_entity(e)

        if dead:
            print(f"[DeathSystem] 移除了 {len(dead)} 个死亡实体")
