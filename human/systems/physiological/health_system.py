#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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