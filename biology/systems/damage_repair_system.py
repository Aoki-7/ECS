#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/damage_repair_system.py
@说明:损伤修复系统

消耗能量修复生物实体的物理损伤。
损伤过高时（>30）通过 phenotype 临时降低光合效率。

修复逻辑：
    - 每点损伤每小时消耗 REPAIR_ENERGY_COST 能量
    - 修复速率受 repair_efficiency 影响
    - 能量不足时修复暂停
"""

from core.system import System
from core.world import World

from biology.components.health_status_component import HealthStatusComponent
from biology.components.energy_component import EnergyComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.traits.trait import Trait


class DamageRepairSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    损伤修复系统

    职责：
        1. 消耗能量修复 HealthStatusComponent 中的伤口
        2. 损伤对 phenotype 产生临时惩罚（光合效率降低）
    """

    # 每点损伤修复消耗的能量
    REPAIR_ENERGY_COST = 0.1
    # 最大每小时修复速率
    MAX_REPAIR_RATE = 0.5

    def __init__(self):
        super().__init__()

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行修复更新

        Args:
            world: World 实例
            dt: 时间步长（小时）
        """
        self._repair_damage(world, dt)
        self._apply_damage_penalty(world)

    def _repair_damage(self, world: World, dt: float):
        """消耗能量修复损伤"""
        for entity, (damage, energy) in world.get_components(
            HealthStatusComponent, EnergyComponent
        ):
            if damage.total_damage <= 0:
                continue

            # 计算修复量
            repair_rate = min(
                self.MAX_REPAIR_RATE,
                damage.repair_efficiency * damage.total_damage * 0.01,
            )
            heal_amount = repair_rate * dt
            energy_cost = heal_amount * self.REPAIR_ENERGY_COST

            if energy.value >= energy_cost:
                energy.value -= energy_cost
                damage.total_damage = max(0.0, damage.total_damage - heal_amount)

                # 更新伤口
                for wound in list(damage.wounds):
                    wound.age += dt
                    # 按严重程度比例分配修复量
                    ratio = wound.severity / max(
                        1.0, damage.total_damage + heal_amount
                    )
                    wound.severity = max(
                        0.0, wound.severity - heal_amount * ratio
                    )

                # 移除已愈合伤口
                damage.wounds = [
                    w for w in damage.wounds if w.severity > 0.1
                ]

    def _apply_damage_penalty(self, world: World):
        """损伤对光合效率的临时惩罚"""
        for entity, (damage, pheno) in world.get_components(
            HealthStatusComponent, PhenotypeComponent
        ):
            if damage.total_damage > 30:
                photo_penalty = min(
                    0.8, (damage.total_damage - 30) / 100
                )
                current_photo = pheno.get(
                    "max_photosynthesis_rate", 20.0
                )
                pheno.set_trait(
                    Trait(
                        name="max_photosynthesis_rate",
                        value=current_photo * (1.0 - photo_penalty),
                        source="damage",
                    )
                )