#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
HealthSystem

职责：
├─ 约束 hp / fatigue 合法范围
├─ 疲劳过高 → 掉血
├─ injury 持续伤害
├─ 低疲劳 → 自动恢复
├─ 极端饥饿/口渴 → 掉血
├─ 体力耗尽 → 掉血
"""

from core.system import System
from core.world import World
from human.components.physiological.health_component import HealthComponent
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
'''
@文件:health_system.py
@说明:身体状态系统
@时间:2026/03/18 18:59:39
@作者:Sherry
@版本:1.0
'''




#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from core.system import System
from core.world import World
from core.entity import Entity
from human.components.physiological.health_component import HealthComponent


class HealthSystem(System):
    """
    健康状态管理系统
    """

    def __init__(self):
        # 疲劳阈值
        self.fatigue_damage_threshold = 80
        self.fatigue_damage_rate = 0.1

        # 自动恢复
        self.recover_threshold = 30
        self.recover_rate = 0.2

        # 饥饿/口渴/体力致死
        self.starvation_damage_rate = 0.5
        self.dehydration_damage_rate = 0.8
        self.exhaustion_damage_rate = 1.0

    def _update(self, world: World, dt: float):
        processed = set()

        # 第一遍：同时有 Health + Needs 的实体
        for entity, [health, needs] in world.get_components(HealthComponent, PhysiologyNeedsComponent):
            processed.add(entity.id)
            self._apply_health_damage(health, needs, dt)

        # 第二遍：只有 Health 没有 Needs 的实体
        for entity, [health] in world.get_components(HealthComponent):
            if entity.id in processed:
                continue
            self._apply_health_damage(health, None, dt)

    def _apply_health_damage(self, health: HealthComponent, needs, dt: float):
        """对单个实体应用健康伤害逻辑"""
        # 数值安全约束
        health.max_hp = max(1, health.max_hp)
        health.hp = max(0.0, min(health.hp, health.max_hp))
        health.fatigue = max(0.0, health.fatigue)

        # 疲劳 → 掉血
        if health.fatigue > self.fatigue_damage_threshold:
            health.hp -= self.fatigue_damage_rate * dt

        # injury 持续伤害
        if health.injury:
            total_damage = 0.0
            for name, effect in health.injury.items():
                dmg = effect.get("damage", 0)
                total_damage += dmg
            health.hp -= total_damage * dt

        # 极端饥饿/口渴/体力耗尽 → 掉血（仅当有 Needs 组件时）
        if needs is not None:
            if needs.hunger >= 90:
                health.hp -= self.starvation_damage_rate * dt * (needs.hunger / 100.0)
            if needs.thirst >= 90:
                health.hp -= self.dehydration_damage_rate * dt * (needs.thirst / 100.0)
            if needs.energy <= 0:
                health.hp -= self.exhaustion_damage_rate * dt

        # 自动恢复
        if health.fatigue < self.recover_threshold and health.hp > 0:
            health.hp += self.recover_rate * dt

        # 最终 clamp
        health.hp = max(0.0, min(health.hp, health.max_hp))
    HealthSystem

    职责：
    ├─ 约束 hp / fatigue 合法范围
    ├─ 疲劳过高 → 掉血
    ├─ injury 持续伤害
    ├─ 低疲劳 → 自动恢复
    """

    def __init__(self):
        # 可调参数（建议后续做成配置）
        self.fatigue_damage_threshold = 80     # 疲劳阈值
        self.fatigue_damage_rate = 0.1         # 每 tick 掉血

        self.recover_threshold = 30            # 恢复阈值
        self.recover_rate = 0.2                # 每 tick 回血

    def update(self, world: World, dt: float):
        """
        :param world: ECS World
        :param dt: 时间步长
        """

        for entity, [health] in world.get_components(HealthComponent):
            health: HealthComponent
            # -------------------------
            # 1. 数值安全约束
            # -------------------------
            health.max_hp = max(1, health.max_hp)
            health.hp = max(0, min(health.hp, health.max_hp))
            health.fatigue = max(0, health.fatigue)

            # -------------------------
            # 2. 疲劳 → 掉血
            # -------------------------
            if health.fatigue > self.fatigue_damage_threshold:
                fatigue_damage = self.fatigue_damage_rate * dt
                health.hp -= fatigue_damage

            # -------------------------
            # 3. injury 持续伤害
            # -------------------------
            if health.injury:
                total_damage = 0
                for name, effect in health.injury.items():
                    dmg = effect.get("damage", 0)
                    total_damage += dmg

                health.hp -= total_damage * dt

            # -------------------------
            # 4. 自动恢复
            # -------------------------
            if health.fatigue < self.recover_threshold and health.hp > 0:
                health.hp += self.recover_rate * dt

            # -------------------------
            # 5. 再次 clamp
            # -------------------------
            health.hp = max(0, min(health.hp, health.max_hp))
