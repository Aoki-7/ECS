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

    # 兼容旧系统：record_place 方法
    def record_place(self, place_id, place_type: str, location=None, time=None, sentiment=None, **kwargs) -> None:
        """record place with optional sentiment"""
        if not isinstance(self.places, dict):
            self.places = {}
        info = {
            'type': place_type,
            'location': location,
            'time': time,
        }
        if sentiment is not None:
            info['sentiment'] = sentiment
        self.places[place_id] = info
    def record_person(self, entity_id: int, name: str, relationship: str = "seen", location=None, time=None) -> None:
        """记录人物到记忆"""
        if not isinstance(self.people, dict):
            self.people = {}
        self.people[entity_id] = {
            'name': name,
            'relationship': relationship,
            'location': location,
            'time': time,
        }

    def has_memory_of(self, place_type: str) -> bool:
        '''check whether a place type is remembered'''
        if not isinstance(self.places, dict):
            return False
        return any(
            isinstance(info, dict) and info.get('type') == place_type
            for info in self.places.values()
        )

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

    # 兼容旧系统：add_event 方法
    def add_event(self, time, event_type, description, impact=0.0, location=None):
        self.events.append({
            'time': time,
            'type': event_type,
            'description': description,
            'impact': impact,
            'location': location,
        })

    # 兼容旧系统：find_best_place_by_type 方法
    def find_best_place_by_type(self, place_type: str):
        """按类型查找最佳地点（返回地点信息或None）"""
        if not isinstance(self.places, dict):
            return None
        
        candidates = []
        for place_id, place_info in self.places.items():
            if isinstance(place_info, dict) and place_info.get('type') == place_type:
                candidates.append((place_id, place_info))
        
        if not candidates:
            return None
        
        # 返回最近访问的地点
        return max(candidates, key=lambda x: x[1].get('time', 0))[0] if candidates else None
        """检查是否有某类记忆"""
        for event in self.events:
            if isinstance(event, dict) and event.get('type') == event_type:
                return True
        return False

    def record_success(self, action_type: str) -> None:
        """记录成功行为"""
        if isinstance(self.recent_successes, dict):
            self.recent_successes[action_type] = self.recent_successes.get(action_type, 0) + 1
