#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@文件:health_system.py
@说明:身体状态系统
@时间:2026/03/18 18:59:39
@作者:Sherry
@版本:2.0
"""

from core.system import System
from core.world import World

from biology.components.health_status_component import HealthStatusComponent

from biology.components.physiology_needs_component import (
    PhysiologyNeedsComponent,
)


class HealthSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    健康状态管理系统

    职责：
    ├─ 约束 hp / fatigue 合法范围
    ├─ 疲劳过高 → 掉血
    ├─ injury 持续伤害
    ├─ 低疲劳 → 自动恢复
    ├─ 极端饥饿/口渴 → 掉血
    ├─ 体力耗尽 → 掉血
    """

    def __init__(self):
        super().__init__()

        # =========================
        # 疲劳伤害
        # =========================
        self.fatigue_damage_threshold = 80.0
        self.fatigue_damage_rate = 0.1

        # =========================
        # 自动恢复
        # =========================
        self.recover_threshold = 30.0
        self.recover_rate = 0.2

        # =========================
        # 生理极限伤害
        # =========================
        self.starvation_damage_rate = 0.5
        self.dehydration_damage_rate = 0.8
        self.exhaustion_damage_rate = 1.0

    # =========================================================
    # ECS Update
    # =========================================================

    def update(self, world: World, dt: float):
        """
        更新健康状态

        Parameters
        ----------
        world : World
            ECS 世界

        dt : float
            时间步长
        """

        # 单次遍历：查询所有 HealthStatusComponent，按需补查 Needs
        for entity, components in world.get_components(HealthStatusComponent):
            health = components[0]
            needs = world.get_component(entity, PhysiologyNeedsComponent)
            self._apply_health_logic(health=health, needs=needs, dt=dt)

    # =========================================================
    # Internal
    # =========================================================

    def _apply_health_logic(
        self,
        health: HealthStatusComponent,
        needs: PhysiologyNeedsComponent | None,
        dt: float,
    ):
        """
        对单个实体应用健康逻辑
        """

        # =====================================================
        # 1. 数值安全约束
        # =====================================================

        health.max_hp = max(1.0, float(health.max_hp))

        health.hp = max(
            0.0,
            min(float(health.hp), health.max_hp)
        )

        # =====================================================
        # 2. 疲劳伤害
        # =====================================================

        fatigue = needs.fatigue if needs else 0.0
        if fatigue >= self.fatigue_damage_threshold:
            fatigue_damage = (
                self.fatigue_damage_rate * dt
            )

            health.hp -= fatigue_damage

        # =====================================================
        # 3. 伤口持续伤害
        # =====================================================

        if health.wounds:
            total_dot = health.update_wounds(dt)
            health.hp -= total_dot

        # =====================================================
        # 4. 生理需求极限伤害
        # =====================================================

        if needs is not None:

            # 饥饿
            if needs.hunger >= 90:
                starvation_damage = (
                    self.starvation_damage_rate
                    * dt
                    * (needs.hunger / 100.0)
                )

                health.hp -= starvation_damage

            # 口渴
            if needs.thirst >= 90:
                dehydration_damage = (
                    self.dehydration_damage_rate
                    * dt
                    * (needs.thirst / 100.0)
                )

                health.hp -= dehydration_damage

            # 精力耗尽
            if needs.energy <= 0:
                exhaustion_damage = (
                    self.exhaustion_damage_rate * dt
                )

                health.hp -= exhaustion_damage

        # =====================================================
        # 5. 自动恢复
        # =====================================================

        can_recover = (
            health.hp > 0
            and fatigue <= self.recover_threshold
        )

        if can_recover:

            recover_amount = (
                self.recover_rate * dt
            )

            health.hp += recover_amount

        # =====================================================
        # 6. 最终 Clamp
        # =====================================================

        health.hp = max(
            0.0,
            min(health.hp, health.max_hp)
        )