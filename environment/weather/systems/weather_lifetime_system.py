#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
天气实体生命周期管理系统

负责清理已过期（remaining_hours <= 0）的天气事件实体。
遵循 ECS 单一职责：仅处理生命周期结束的清理，不参与业务逻辑判断。

清理规则：
- 所有 LifetimeComponent.remaining_hours <= 0 的实体都会被清理
- 允许通过 event_type_blacklist 参数配置保留的事件类型
  （如 drought / cold_wave 等持续型事件可由其他系统管理）
"""

from core.world import World
from core.system import System
from environment.weather.components.weather_modifier_component import (
    WeatherEventTagComponent,
    LifetimeComponent,
    WeatherModifierComponent,
)

from typing import List, Optional, Tuple, Set


class WeatherLifetimeSystem(System):
    """天气实体生命周期系统

    定期检查所有携带 LifetimeComponent 的实体，
    清理已过期（remaining_hours <= 0）的事件实体。

    持续型事件（如 drought/cold_wave）可通过 blacklist 跳过清理，
    由外部系统手动管理。
    """

    def __init__(
        self,
        event_type_blacklist: Optional[Set[str]] = None,
    ):
        """
        Args:
            event_type_blacklist: 持续型事件类型列表，这些类型即使过期也不自动清理。
                                  例如 {"drought", "cold_wave"}。
        """
        self.event_type_blacklist = event_type_blacklist or set()

    def update(self, world: World, delta_hours: float):
        """生命周期更新

        1. 遍历所有携带 (WeatherEventTagComponent, LifetimeComponent) 的实体
        2. 消耗其 remaining_hours
        3. 清理已过期且不在黑名单中的实体
        """
        expired_entities = self._collect_expired_entities(world)

        for entity in expired_entities:
            self._cleanup_entity(world, entity)

    def _collect_expired_entities(self, world: World) -> List:
        """收集所有已过期且应被清理的实体"""
        expired = []

        entities = list(
            world.get_components(WeatherEventTagComponent, LifetimeComponent)
        )

        for entity, [tag, lifetime] in entities:
            if tag and lifetime:
                # 消耗剩余时间
                lifetime.remaining_hours -= world.delta_hours if hasattr(world, 'delta_hours') else 1.0

                if lifetime.remaining_hours <= 0:
                    # 检查是否在黑名单中（持续型事件）
                    if tag.event_type in self.event_type_blacklist:
                        # 持续型事件：重置而非清理
                        print(
                            f"[WeatherLifetimeSystem] 持续型事件 \"{tag.name}\" "
                            f"已过期但由黑名单保护，不自动清理"
                        )
                    else:
                        expired.append(entity)

        return expired

    def _cleanup_entity(self, world: World, entity):
        """清理指定事件实体"""
        tag = world.get_component(entity, WeatherEventTagComponent)
        if tag:
            event_name = tag.name if hasattr(tag, 'name') else tag.event_type
            print(f"[WeatherLifetimeSystem] 清理事件: {event_name} (entity={entity.id})")

        world.remove_entity(entity)


__all__ = ['WeatherLifetimeSystem']
