#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:memory_component.py
@说明:记忆组件 v4.0 — 纯数据化
@时间:2026/06/12
@作者:AI Assistant
@版本:4.0

v4.0 变更：
- 所有业务逻辑迁移到 MemoryManagementSystem
- Component 仅保留数据字段
'''

from dataclasses import dataclass, field

from core.component import Component
from core.component_serializer import register_component


@register_component
@dataclass(slots=True)
class MemoryComponent(Component):
    """
    记忆组件 — 纯数据

    存储事件、地点和人物记忆，影响决策。
    所有业务逻辑由 MemoryManagementSystem 处理。
    """
    # 事件记忆: [(time, type, description, impact, location)]
    # type: "found_water", "found_food", "socialized", "fought", "paired", "birth", "death", "slept", "explored"
    # impact: -1 (负面) ~ 1 (正面)
    events: list = field(default_factory=list)

    # 地点记忆: {(x, y): {"type": "water_source", "last_visit": time, "sentiment": 0.5, "visits": 1}}
    places: dict = field(default_factory=dict)

    # 人物记忆: {entity_id: {"name": str, "relationship": str, "last_interaction": time, "trust": 0.5, "events": []}}
    people: dict = field(default_factory=dict)

    # 最近成功的行动类型（用于强化学习）
    recent_successes: dict = field(default_factory=lambda: {
        "find_water": 0,
        "find_food": 0,
        "socialize": 0,
        "explore": 0,
        "rest": 0,
    })

    # 数据约束（非业务逻辑）
    MAX_EVENTS: int = 100
    MAX_PEOPLE: int = 50

    def to_dict(self) -> dict:
        return {
            "events": self.events,
            "places": self.places,
            "people": self.people,
            "recent_successes": self.recent_successes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryComponent":
        return cls(
            events=data.get("events", []),
            places=data.get("places", {}),
            people=data.get("people", {}),
            recent_successes=data.get("recent_successes", {
                "find_water": 0,
                "find_food": 0,
                "socialize": 0,
                "explore": 0,
                "rest": 0,
            }),
        )
