#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:life_cycle_system.py
@说明:生命周期推进系统，根据累积积温/年龄推进生命阶段
@时间:2026/05/28
@版本:1.0
'''

from typing import Dict

from core.world import World
from core.system import System
from core.event_log_component import EventLog

from biology.components.life_cycle_component import LifeCycleComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.components.energy_component import EnergyComponent
from biology.components.morphology_component import MorphologyComponent
from biology.components.genome_component import GenomeComponent


class LifeCycleSystem(System):
    """
    生命周期推进系统

    依赖：
        - LifeCycleComponent（必要）
        - EnvironmentComponent（用于获取温度计算 GDD）

    功能：
        - 累积有效积温（GDD）
        - 按年龄/GDD 推进生命阶段
        - 触发阶段转换事件
    """

    def __init__(self):
        super().__init__()
        self.enable_log = True

    def update(self, world: World, dt: float = 1.0):
        """
        每帧更新生命周期

        参数：
            dt: 时间步长（小时）
        """
        env = world.get_environment()

        if env is None:
            air_temp = 25.0
        else:
            air_temp = env.air_temperature

        # 基准温度（低于该温度不积累 GDD）
        base_temp = 10.0

        for entity, (lifecycle,) in world.get_components(LifeCycleComponent):
            lifecycle: LifeCycleComponent

            if lifecycle.is_dead:
                continue

            # ========== 1. 累积生存时间 ==========
            lifecycle.current_age += dt

            # ========== 2. 累积有效积温 ==========
            if air_temp > base_temp:
                gdd_increment = (air_temp - base_temp) * (dt / 24.0)
                lifecycle.gdd_accumulated += gdd_increment

            # ========== 3. 阶段推进逻辑 ==========
            old_stage = lifecycle.stage
            self._advance_stage_if_ready(lifecycle)
            new_stage = lifecycle.stage

            # ========== 4. 阶段变更事件 ==========
            if old_stage != new_stage:
                self._on_stage_change(world, entity, lifecycle, old_stage, new_stage)

    # -------------------------------------------------
    # 阶段推进核心
    # -------------------------------------------------

    def _advance_stage_if_ready(self, lifecycle: LifeCycleComponent):
        """检查并推进生命周期阶段"""

        def _check_gdd(lc: LifeCycleComponent, min_stage: int) -> bool:
            """检查积温是否达到某阶段阈值（若未配置则跳过 GDD 检查）"""
            req = lc.gdd_requirements.get(min_stage)
            if req is None:
                return False
            return lc.gdd_accumulated >= req

        def _check_age(lc: LifeCycleComponent, stage_idx: int) -> bool:
            """检查年龄是否超过阶段时长阈值"""
            if stage_idx >= len(lc.stage_durations):
                return True
            return lc.current_age >= lc.stage_durations[stage_idx]

        transitions = [
            # (当前阶段, 下一阶段, 条件函数)
            (LifeCycleComponent.SEED, LifeCycleComponent.SPROUT,
             lambda lc: _check_age(lc, 0) or _check_gdd(lc, LifeCycleComponent.SPROUT)),

            (LifeCycleComponent.SPROUT, LifeCycleComponent.VEGETATIVE,
             lambda lc: _check_gdd(lc, LifeCycleComponent.VEGETATIVE) or _check_age(lc, 1)),

            (LifeCycleComponent.VEGETATIVE, LifeCycleComponent.MATURE,
             lambda lc: _check_gdd(lc, LifeCycleComponent.MATURE) or _check_age(lc, 2)),

            (LifeCycleComponent.MATURE, LifeCycleComponent.SENESCENCE,
             lambda lc: lc.current_age >= lc.max_age or lc.senescence_triggered),

            (LifeCycleComponent.SENESCENCE, LifeCycleComponent.DEAD,
             lambda lc: lc.current_age >= lc.max_age + lc.stage_durations[4]),
        ]

        for current_stage, next_stage, condition in transitions:
            if lifecycle.stage == current_stage and condition(lifecycle):
                lifecycle.set_stage(next_stage)
                break

    # -------------------------------------------------
    # 阶段变更回调
    # -------------------------------------------------

    def _on_stage_change(
        self,
        world: World,
        entity,
        lifecycle: LifeCycleComponent,
        old_stage: int,
        new_stage: int,
    ):
        """阶段变更时执行额外操作"""
        if not self.enable_log:
            return

        old_name = LifeCycleComponent.STAGE_NAMES.get(old_stage, "未知")
        new_name = LifeCycleComponent.STAGE_NAMES.get(new_stage, "未知")

        EventLog.log(
            world,
            event_type="lifecycle",
            description=f"植物 E{entity.id} 进入 {new_name} (之前: {old_name})",
            entity_id=entity.id,
            data={
                "old_stage": old_stage,
                "new_stage": new_stage,
                "age": lifecycle.current_age,
                "gdd": lifecycle.gdd_accumulated,
            },
            severity="info"
        )
