#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/senescence_system.py
@说明:衰老系统，驱动植物进入衰老并逐步退化

作用：
    - 植物进入衰老期后，逐步降低光合效率
    - 黄化叶片、枯萎
    - 能量入不敷出加速死亡

触发条件（由 LifeCycleSystem 推进）：
    - 超龄（current_age >= max_age）
    - 长期能量为负（energy.value <= 0 且仍存活）
    - 环境胁迫累积
"""

from core.world import World
from core.system import System

from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.traits.trait import Trait


class SenescenceSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    衰老系统

    职责：
        1. 处理已进入 SENESCENCE 阶段的实体，逐步退化其生理状态
        2. 检测长期能量不足的存活实体，触发 senescence_triggered 标志
           （供 LifeCycleSystem 在下一帧推进到 SENESCENCE 阶段）
    """

    def __init__(self):
        super().__init__()

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        更新衰老状态

        Args:
            world: World 实例
            dt: 时间步长（小时）
        """
        # ========== 衰老植物：退化生长 & 光合 ==========
        for entity, (lifecycle, pheno, energy, morph) in \
                world.get_components(
                    LifeCycleComponent,
                    PhenotypeComponent,
                    EnergyComponent,
                    MorphologyComponent
                ):
            self._process_senescence(entity, lifecycle, pheno, energy, morph, dt)

        # ========== 能量耗尽触发衰老标志 ==========
        for entity, (lifecycle, energy) in \
                world.get_components(LifeCycleComponent, EnergyComponent):

            # 跳过已在衰老/死亡的实体
            if lifecycle.is_senescence or lifecycle.is_dead:
                continue

            # 长期能量不足 → 触发衰老
            if energy.value <= 0 and lifecycle.is_alive:
                lifecycle.senescence_triggered = True

    # -------------------------------------------------
    # 衰老处理细节
    # -------------------------------------------------

    def _process_senescence(
        self,
        entity,
        lifecycle: LifeCycleComponent,
        pheno: PhenotypeComponent,
        energy: EnergyComponent,
        morph: MorphologyComponent,
        dt: float,
    ):
        """
        衰老期间的逐帧退化

        退化程度与衰老持续时间成正比（senescence_ratio: 0→1）。
        """
        if not lifecycle.is_senescence:
            return

        # 衰老系数（随衰老时间递增）
        senescence_duration = lifecycle.current_age - lifecycle.max_age
        senescence_ratio = min(1.0, senescence_duration / 100.0)

        if senescence_ratio <= 0:
            return

        # ---------- 形态退化 ----------
        # 叶片黄化
        morph.yellowing = min(1.0, senescence_ratio)
        # 枯萎
        morph.wilting = min(1.0, senescence_ratio * 0.5)

        # ---------- 光合效率衰减 ----------
        current_photo = pheno.get("max_photosynthesis_rate", 20.0)

        if current_photo > 0:
            senesced_photo = current_photo * (1.0 - senescence_ratio * 0.8)
            # 更新表型中的光合速率值（来源标记为 senescence）
            pheno.set_trait(Trait(
                name="max_photosynthesis_rate",
                value=max(0.5, senesced_photo),
                source="senescence"
            ))

        # ---------- 能量持续流失 ----------
        # 衰老期维护成本上升
        maintenance_cost = senescence_ratio * 0.5 * dt
        energy.value = max(-10.0, energy.value - maintenance_cost)
