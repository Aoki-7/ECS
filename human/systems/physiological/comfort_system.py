#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:comfort_system.py
@说明:舒适度与疲劳环境系统（拆分自 PhysiologyNeedsSystem）
@时间:2026/05/29
@版本:1.0
'''

from core.system import System
from core.world import World

from environment.environment_component import EnvironmentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent


class ComfortSystem(System):
    """
    舒适度系统
    负责舒适度和疲劳的环境耦合（高温、高湿、降雨）
    """

    def update(self, world: World, dt: float):
        env = world.get_environment()
        if not isinstance(env, EnvironmentComponent):
            return

        for entity, (needs,) in world.get_components(PhysiologyNeedsComponent):
            needs: PhysiologyNeedsComponent

            # 高温增加疲劳
            if env.air_temperature > 25.0:
                needs.fatigue += 0.5 * (env.air_temperature - 25.0) * dt

            # 高湿度降低舒适度
            if env.air_humidity > 0.9:
                needs.comfort -= 0.3 * dt

            # Clamp
            needs.fatigue = max(0.0, min(needs.max_fatigue, needs.fatigue))
            needs.comfort = max(0.0, min(needs.max_comfort, needs.comfort))
