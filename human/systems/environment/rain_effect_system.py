#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
RainEffectSystem - 降雨效果系统

降雨 >10mm：舒适度下降
"""

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from space.space_component import SpaceComponent


class RainEffectSystem(System):
    """降雨对实体的影响"""

    priority = 25

    # 魔法值常量
    RAIN_THRESHOLD = 10.0        # 降雨阈值 mm
    COMFORT_PENALTY = 0.5        # 舒适度下降系数

    def update(self, world: World, dt: float):
        super().update(world, dt)
        env = world.get_environment()
        if not isinstance(env, EnvironmentComponent):
            return

        rainfall = env.rainfall
        if rainfall <= self.RAIN_THRESHOLD:
            return

        for entity, (needs, space) in world.get_components(
            PhysiologyNeedsComponent, SpaceComponent
        ):
            needs.comfort -= self.COMFORT_PENALTY * dt
            needs.comfort = max(0.0, min(needs.max_comfort, needs.comfort))
