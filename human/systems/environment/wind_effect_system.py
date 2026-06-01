#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
WindEffectSystem - 强风效果系统

风速 >10m/s：疲劳增加
"""

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from space.space_component import SpaceComponent


class WindEffectSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """强风对实体的影响"""

    priority = 25

    # 魔法值常量
    WIND_THRESHOLD = 10.0        # 强风阈值 m/s
    FATIGUE_RATE = 0.3           # 疲劳增长系数

    def update(self, world: World, dt: float):
        super().update(world, dt)
        env = world.get_environment()
        if not isinstance(env, EnvironmentComponent):
            return

        wind = env.wind_speed
        if wind <= self.WIND_THRESHOLD:
            return

        for entity, (needs, space) in world.get_components(
            PhysiologyNeedsComponent, SpaceComponent
        ):
            needs.fatigue += self.FATIGUE_RATE * dt
            needs.fatigue = max(0.0, min(needs.max_fatigue, needs.fatigue))
