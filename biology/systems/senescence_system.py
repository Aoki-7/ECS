#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:senescence_system.py
@说明:衰老系统，驱动植物进入衰老并逐步退化
@时间:2026/05/28
@版本:1.0
'''

from core.world import World
from core.system import System

from biology.components.life_cycle_component import LifeCycleComponent
from biology.components.energy_component import EnergyComponent
from biology.components.morphology_component import MorphologyComponent
from biology.components.phenotype_component import PhenotypeComponent


class SenescenceSystem(System):
    """
    衰老系统

    作用：
    - 植物进入衰老期后，逐步降低光合效率
    - 黄化叶片、枯萎
    - 能量入不敷出加速死亡

    触发条件（由 LifeCycleSystem 推进）：
    - 超龄（current_age >= max_age）
    - 长期能量为负
    - 环境胁迫累积
    """

    def __init__(self):
        super().__init__()

    def update(self, world: World, dt: float = 1.0):
        """
        更新衰老状态

        只处理已进入 SENESCENCE 阶段的实体
        """
        # ========== 衰老植物：退化生长&光合 ==========
        for entity, (lifecycle, pheno, energy, morph) in \
                world.get_components(
                    LifeCycleComponent,
                    PhenotypeComponent,
                    EnergyComponent,
                    MorphologyComponent
                ):
            self._process_senescence(entity, lifecycle, pheno, energy, morph, dt)

        # ========== 能量耗尽触发衰老 ==========
        for entity, (lifecycle, energy) in \
                world.get_components(LifeCycleComponent, EnergyComponent):

            # 跳过已有生命周期组件（已在上面处理过）或已在衰老/死亡
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
        """衰老期间的逐帧退化"""

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
        # 从表型中获取光合速率，衰老期按比例衰减
        current_photo = pheno.get("max_photosynthesis_rate", 20.0)

        if current_photo > 0:
            senesced_photo = current_photo * (1.0 - senescence_ratio * 0.8)
            # 更新表型中的光合速率值
            from biology.traits.trait import Trait
            pheno.set_trait(Trait(
                name="max_photosynthesis_rate",
                value=max(0.5, senesced_photo),
                source="senescence"
            ))

        # ---------- 能量持续流失 ----------
        # 衰老期维护成本上升
        maintenance_cost = senescence_ratio * 0.5 * dt
        energy.value = max(-10.0, energy.value - maintenance_cost)
