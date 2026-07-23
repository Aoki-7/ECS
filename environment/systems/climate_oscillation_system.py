#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
气候震荡系统

管理 ClimateOscillationComponent 的生命周期：
- 递减 remaining_days
- 将震荡异常叠加到世界 ClimateComponent
- 震荡结束时移除组件
"""

from core.system import System
from core.world import World

from environment.climate.climate_component import ClimateComponent
from environment.climate.climate_oscillation_component import ClimateOscillationComponent


class ClimateOscillationSystem(System):
    """气候震荡事件系统"""

    tick_interval = 1
    priority = 15  # 在气候系统之前

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)
        climate = world.get_world_component(ClimateComponent)
        if climate is None:
            return

        # 假设震荡组件挂载在世界实体上
        world_entity = world.get_world_entity()
        oscillation = world.get_component(world_entity, ClimateOscillationComponent) if world_entity else None
        if oscillation is None:
            return

        # 应用异常
        climate.temp_trend += oscillation.temperature_anomaly * 0.001
        climate.humidity_trend += oscillation.precipitation_anomaly * 0.001
        climate.rainfall_trend += oscillation.precipitation_anomaly * 0.001

        # 递减剩余天数
        oscillation.remaining_days = max(0, oscillation.remaining_days - int(dt))
        if oscillation.remaining_days <= 0:
            world.remove_component(world_entity, ClimateOscillationComponent)