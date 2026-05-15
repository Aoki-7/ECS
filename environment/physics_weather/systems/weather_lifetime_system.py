#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
天气实体生命周期管理系统 — 从 old weather/ 迁移至 physics_weather/

负责清理已过期的极端天气事件实体。
"""

from typing import List, Optional, Set

from core.world import World
from core.system import System
from environment.physics_weather.components.weather_event_components import (
    WeatherEventTagComponent,
    ExtremeWeatherLifetimeComponent,
    WeatherModifierComponent,
)

LifetimeComponent = ExtremeWeatherLifetimeComponent


class WeatherLifetimeSystem(System):
    """天气实体生命周期系统"""

    def __init__(self, event_type_blacklist: Optional[Set[str]] = None):
        self.event_type_blacklist = event_type_blacklist or set()

    def update(self, world: World, delta_hours: float):
        expired_entities = self._collect_expired_entities(world)
        for entity in expired_entities:
            self._cleanup_entity(world, entity)

    def _collect_expired_entities(self, world: World) -> List:
        expired = []
        entities = list(world.get_components(WeatherEventTagComponent, LifetimeComponent))

        for entity, [tag, lifetime] in entities:
            if tag and lifetime:
                lifetime.remaining_hours -= 1.0
                if lifetime.remaining_hours <= 0:
                    if tag.event_type in self.event_type_blacklist:
                        print(
                            f"[WeatherLifetimeSystem] 持续型事件 \"{tag.name}\" "
                            f"已过期但由黑名单保护，不自动清理"
                        )
                    else:
                        expired.append(entity)
        return expired

    def _cleanup_entity(self, world: World, entity) -> None:
        """清理一个实体及其所有组件"""
        tag = world.get_component(entity, WeatherEventTagComponent)
        event_name = tag.name if tag else "unknown"
        print(f"[WeatherLifetimeSystem] 天气事件 \"{event_name}\" 已结束，清理实体")
        world.remove_entity(entity)
