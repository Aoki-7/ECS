#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:age_system.py
@说明:年龄增长系统
@时间:2026/05/26
@版本:1.0
'''

from core.system import System
from core.world import World

from biology.lifecycle.components.life_cycle_component import LifeCycleComponent


class AgeSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    年龄增长系统

    每步推进 LifeCycleComponent.current_age。
    时间压缩：每模拟步（1小时）≈ 0.05年（约18天），
    使新生儿在约360步后达到生育年龄（18岁），
    成年人在约140步后进入衰老（从18岁到25岁）。
    """

    # 每步增长的年数（时间压缩）：每模拟小时 0.01 年 ≈ 3.65 天
    YEAR_PER_STEP: float = 0.01

    def update(self, world: World, dt: float):
        for entity, [age] in world.get_components(LifeCycleComponent):
            age: LifeCycleComponent
            age.current_age += self.YEAR_PER_STEP * dt