#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物需求系统

驱动动物的基本生理需求：
    1. 饥饿度随时间自然增长（受代谢率影响）
    2. 口渴度随时间自然增长（受环境温度影响）
    3. 困倦度随活动时间增长
    4. 恐惧度在遭遇威胁时激增
    5. 繁殖欲望在成熟期达到峰值

与 GrazingSystem / PredationSystem 的关系：
    - NeedsSystem 驱动动物产生觅食/捕食动机
    - 觅食/捕食成功后降低 hunger
    - 高 fear 会抑制觅食行为，触发逃跑
"""

from core.system import System
from core.world import World

from biology.organisms.animal.components.animal_component import AnimalComponent
from biology.organisms.animal.components.animal_needs_component import AnimalNeedsComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from biology.components.phenotype_component import PhenotypeComponent
from space.space_component import SpaceComponent

import logging

logger = logging.getLogger(__name__)


class AnimalNeedsSystem(System):
    tick_interval = 5

    @staticmethod
    def get_dominant_need(needs: AnimalNeedsComponent) -> str:
        """返回当前最强烈的需求名称"""
        needs_dict = {
            "hunger": needs.hunger,
            "thirst": needs.thirst,
            "sleepiness": needs.sleepiness,
            "fear": needs.fear,
            "reproductive_urge": needs.reproductive_urge,
        }
        return max(needs_dict, key=needs_dict.get)

    @staticmethod
    def is_critical(needs: AnimalNeedsComponent, threshold: float = 0.8) -> bool:
        """是否有任何需求达到临界值"""
        return any(
            v >= threshold
            for v in [needs.hunger, needs.thirst, needs.sleepiness, needs.fear]
        )

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新所有动物的需求状态"""
        for entity, (animal, needs, energy) in world.get_components(
            AnimalComponent, AnimalNeedsComponent, EnergyComponent
        ):
            pheno = world.get_component(entity, PhenotypeComponent)
            if pheno is None:
                pheno = PhenotypeComponent()  # 使用默认表型
            self._update_hunger(needs, energy, pheno, dt)
            self._update_thirst(needs, pheno, dt)
            self._update_sleepiness(needs, animal, dt)
            self._update_reproductive_urge(needs, animal, dt)
            self._decay_fear(needs, dt)

    def _update_hunger(
        self, needs: AnimalNeedsComponent, energy: EnergyComponent,
        pheno: PhenotypeComponent, dt: float
    ) -> None:
        """更新饥饿度：能量越低，饥饿度越高"""
        metabolism = PhenotypeSystem.get(pheno, "metabolism_rate", 0.02) if pheno else 0.02
        max_energy = getattr(energy, "max_energy", 100.0)
        energy_ratio = energy.value / max_energy if max_energy > 0 else 1.0

        # 饥饿度与能量成反比，代谢率越高增长越快
        hunger_increase = (1.0 - energy_ratio) * metabolism * 5.0 * dt
        needs.hunger = min(1.0, needs.hunger + hunger_increase)

        # 若能量充足，饥饿度自然下降
        if energy_ratio > 0.8:
            needs.hunger = max(0.0, needs.hunger - 0.05 * dt)

    def _update_thirst(
        self, needs: AnimalNeedsComponent, pheno: PhenotypeComponent, dt: float
    ) -> None:
        """更新口渴度：基础增长 + 代谢影响"""
        metabolism = PhenotypeSystem.get(pheno, "metabolism_rate", 0.02) if pheno else 0.02
        thirst_increase = 0.01 * metabolism * 50.0 * dt
        needs.thirst = min(1.0, needs.thirst + thirst_increase)

    def _update_sleepiness(
        self, needs: AnimalNeedsComponent, animal: AnimalComponent, dt: float
    ) -> None:
        """更新困倦度：年龄越大越易疲劳"""
        age_factor = min(1.0, animal.age / max(animal.max_age, 1.0))
        sleep_increase = (0.005 + age_factor * 0.01) * dt
        needs.sleepiness = min(1.0, needs.sleepiness + sleep_increase)

    def _update_reproductive_urge(
        self, needs: AnimalNeedsComponent, animal: AnimalComponent, dt: float
    ) -> None:
        """更新繁殖欲望：仅成年动物有繁殖需求"""
        if not animal.is_adult:
            needs.reproductive_urge = 0.0
            return

        # 繁殖欲望自然增长，达到峰值后波动
        urge_increase = 0.002 * dt
        needs.reproductive_urge = min(1.0, needs.reproductive_urge + urge_increase)

    def _decay_fear(self, needs: AnimalNeedsComponent, dt: float) -> None:
        """恐惧度自然衰减"""
        if needs.fear > 0:
            needs.fear = max(0.0, needs.fear - 0.1 * dt)