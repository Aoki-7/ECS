#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:life_cycle_component.py
@说明:生命周期阶段组件，管理生物从出生到死亡的各阶段
@时间:2026/05/28
@版本:1.0
'''

from typing import Optional, List

from core.component import Component


class LifeCycleComponent(Component):
    """
    生命周期阶段组件

    管理生物所处的生命阶段及相关参数。
    适用于植物、动物等所有有生命周期的 entity。

    生命周期阶段（按数值大小排序）：
        SEED        = 0   种子/休眠
        SPROUT      = 1   发芽/幼苗期
        VEGETATIVE  = 2   营养生长期
        MATURE      = 3   成熟期（可繁殖）
        SENESCENCE  = 4   衰老期
        DEAD        = 5   死亡

    阶段推进条件由 LifeCycleSystem 控制。
    """

    # 阶段常量
    SEED = 0
    SPROUT = 1
    VEGETATIVE = 2
    MATURE = 3
    SENESCENCE = 4
    DEAD = 5

    STAGE_NAMES = {
        0: "种子",
        1: "幼苗",
        2: "营养生长期",
        3: "成熟期",
        4: "衰老期",
        5: "死亡",
    }

    __slots__ = (
        "stage", "current_age", "max_age",
        "min_reproductive_age", "max_reproductive_age",
        "stage_durations", "gdd_accumulated",
        "gdd_requirements", "senescence_triggered", "death_reason",
    )

    def __init__(
        self,
        stage: int = 0,
        current_age: float = 0.0,
        max_age: float = 100.0,
        stage_durations: Optional[list] = None,
        gdd_requirements: Optional[dict] = None,
    ):
        # 生命阶段
        self.stage = stage

        # 当前生存时间（小时）
        self.current_age = current_age

        # 最大寿命（小时），超过自动进入衰老
        self.max_age = max_age

        # 生育年龄范围（从 AgeComponent 迁入）
        self.min_reproductive_age = 18.0
        self.max_reproductive_age = 50.0

        # 各阶段持续时间阈值（小时）
        # [seed, sprout, vegetative, mature, senescence]
        self.stage_durations = (
            stage_durations
            if stage_durations is not None
            else [10.0, 20.0, 100.0, 200.0, 50.0]
        )

        # 累计有效积温（生长度日 GDD）
        self.gdd_accumulated = 0.0

        # 各阶段所需积温阈值
        self.gdd_requirements = (
            gdd_requirements
            if gdd_requirements is not None
            else {
                self.SEED: 10.0,
                self.SPROUT: 30.0,
                self.VEGETATIVE: 80.0,
                self.MATURE: 0.0,
            }
        )

        # 衰老触发标志（由特定条件设置）
        self.senescence_triggered = False

        # 死亡原因（DeathSystem 填写）
        self.death_reason = None

    # === 阶段判断 ===

    @property
    def is_seed(self) -> bool:
        return self.stage == self.SEED

    @property
    def is_sprout(self) -> bool:
        return self.stage == self.SPROUT

    @property
    def is_vegetative(self) -> bool:
        return self.stage == self.VEGETATIVE

    @property
    def is_mature(self) -> bool:
        return self.stage == self.MATURE

    @property
    def is_senescence(self) -> bool:
        return self.stage == self.SENESCENCE

    @property
    def is_dead(self) -> bool:
        return self.stage == self.DEAD

    @property
    def is_alive(self) -> bool:
        return self.stage < self.SENESCENCE

    @property
    def stage_name(self) -> str:
        return self.STAGE_NAMES.get(self.stage, "未知")

    # === 年龄别名与辅助（从 AgeComponent 迁入） ===

    @property
    def age(self) -> float:
        """年龄别名，兼容原 AgeComponent.age 接口"""
        return self.current_age

    @age.setter
    def age(self, value: float):
        self.current_age = value

    def is_reproductive_age(self) -> bool:
        """检查是否处于可生育年龄"""
        return self.min_reproductive_age <= self.current_age <= self.max_reproductive_age

    # === 阶段推进 ===

    def advance_stage(self):
        """推进到下一个生命阶段"""
        if self.stage < self.DEAD:
            self.stage += 1

    def set_stage(self, stage: int):
        """直接设置阶段（用于系统驱动）"""
        if 0 <= stage <= self.DEAD:
            self.stage = stage
