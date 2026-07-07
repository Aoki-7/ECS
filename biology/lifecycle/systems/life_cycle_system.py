#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
生命周期系统

将 LifeCycleComponent 中的业务逻辑迁移到 System
'''

from core.system import System
from core.world import World

from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from human.components.basic.human_component import HumanComponent


class LifeCycleSystem(System):
    """生命周期管理系统"""

    tick_interval = 20  # 每20帧执行一次

    def update(self, world: World, dt: float):
        for entity, (life,) in world.get_components(LifeCycleComponent):
            # 人类年龄由 AgeSystem 按时间压缩比例推进，避免与本系统的小时尺度冲突
            if world.has_component(entity, HumanComponent):
                self._check_death(life)
                continue
            self._update_age(life, dt)
            self._check_stage_advance(life)
            self._check_death(life)

    def _update_age(self, life: LifeCycleComponent, dt: float):
        """更新年龄"""
        if life.stage != LifeCycleComponent.DEAD:
            life.current_age += dt

    @staticmethod
    def is_reproductive_age(life: LifeCycleComponent) -> bool:
        """判断是否为生育年龄"""
        return life.min_reproductive_age <= life.current_age <= life.max_reproductive_age

    @staticmethod
    def is_seed(life: LifeCycleComponent) -> bool:
        """是否为种子阶段"""
        return life.stage == LifeCycleComponent.SEED

    def _check_stage_advance(self, life: LifeCycleComponent):
        """检查阶段推进"""
        if life.stage == LifeCycleComponent.DEAD:
            return

        # 检查是否超过当前阶段持续时间
        if life.stage < len(life.stage_durations):
            required_duration = life.stage_durations[life.stage]
            if life.current_age >= required_duration:
                self._advance_stage(life)

        # 检查 GDD 条件（仅对植物）
        if life.gdd_requirements and life.stage in life.gdd_requirements:
            required_gdd = life.gdd_requirements[life.stage]
            if life.gdd_accumulated >= required_gdd:
                self._advance_stage(life)

    def _advance_stage(self, life: LifeCycleComponent):
        """推进到下一阶段"""
        if life.stage < LifeCycleComponent.DEAD:
            life.stage += 1

    def _check_death(self, life: LifeCycleComponent):
        """检查死亡条件"""
        if life.stage == LifeCycleComponent.DEAD:
            return

        # 超过最大寿命
        if life.current_age >= life.max_age:
            life.stage = LifeCycleComponent.DEAD
            life.death_reason = "old_age"
            return

        # 衰老触发
        if life.senescence_triggered and life.stage < LifeCycleComponent.SENESCENCE:
            life.stage = LifeCycleComponent.SENESCENCE

    # === 静态工具方法 ===

    @staticmethod
    def is_seed(life: LifeCycleComponent) -> bool:
        return life.stage == LifeCycleComponent.SEED

    @staticmethod
    def is_sprout(life: LifeCycleComponent) -> bool:
        return life.stage == LifeCycleComponent.SPROUT

    @staticmethod
    def is_vegetative(life: LifeCycleComponent) -> bool:
        return life.stage == LifeCycleComponent.VEGETATIVE

    @staticmethod
    def is_mature(life: LifeCycleComponent) -> bool:
        return life.stage == LifeCycleComponent.MATURE

    @staticmethod
    def is_senescence(life: LifeCycleComponent) -> bool:
        return life.stage == LifeCycleComponent.SENESCENCE

    @staticmethod
    def is_dead(life: LifeCycleComponent) -> bool:
        return life.stage == LifeCycleComponent.DEAD

    @staticmethod
    def is_alive(life: LifeCycleComponent) -> bool:
        return life.stage != LifeCycleComponent.DEAD

    @staticmethod
    def stage_name(life: LifeCycleComponent) -> str:
        return LifeCycleComponent.STAGE_NAMES.get(life.stage, "未知")

    @staticmethod
    def is_reproductive_age(life: LifeCycleComponent) -> bool:
        return (
            life.stage == LifeCycleComponent.MATURE
            and life.min_reproductive_age <= life.current_age <= life.max_reproductive_age
        )
