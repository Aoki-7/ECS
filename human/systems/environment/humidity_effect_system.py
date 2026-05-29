#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
HumidityEffectSystem - 湿度效果系统

湿度 <30%：口渴加剧
湿度 >90%：舒适度下降
"""

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from space.space_component import SpaceComponent


class HumidityEffectSystem(System):
    """湿度对实体的影响"""

    priority = 25

    # 魔法值常量
    HUMIDITY_LOW = 0.30          # 低湿度阈值
    HUMIDITY_HIGH = 0.90         # 高湿度阈值
    THIRST_RATE = 0.5            # 低湿度口渴系数
    COMFORT_PENALTY = 0.3        # 高湿度舒适系数

    def update(self, world: World, dt: float):
        super().update(world, dt)
        env = world.get_environment()
        if not isinstance(env, EnvironmentComponent):
            return

        humidity = env.air_humidity

        for entity, (needs, space) in world.get_components(
            PhysiologyNeedsComponent, SpaceComponent
        ):
            if humidity < self.HUMIDITY_LOW:
                needs.thirst += self.THIRST_RATE * dt

            if humidity > self.HUMIDITY_HIGH:
                needs.comfort -= self.COMFORT_PENALTY * dt

            # Clamp
            needs.thirst = max(0.0, min(needs.max_thirst, needs.thirst))
            needs.comfort = max(0.0, min(needs.max_comfort, needs.comfort))
