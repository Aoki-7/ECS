#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:memory_component.py
@说明:记忆组件 v2.0
@时间:2026/03/13
@作者:Sherry
@版本:2.0

增强版记忆系统：
- 事件记忆（带时间、类型、描述、情感影响）
- 地点记忆（带类型、最后访问时间、情感）
- 人物记忆（带关系、最后互动时间、信任度）
- 情绪衰减和最近事件查询
'''

from dataclasses import dataclass, field

from core.component import Component

@dataclass
class MemoryComponent(Component):
    """
    记忆组件
    存储事件、地点和人物记忆，影响决策
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
    
    def add_event(self, time: float, event_type: str, description: str, 
                  impact: float = 0.0, location: tuple = None):
        """
        添加事件记忆
        
        Args:
            time: 发生时间（总小时）
            event_type: 事件类型
            description: 描述
            impact: 情感影响 (-1 ~ 1)
            location: 发生位置 (x, y)
        """
        self.events.append({
            "time": time,
            "type": event_type,
            "description": description,
            "impact": impact,
            "location": location,
        })
        # 只保留最近100条
        if len(self.events) > 100:
            self.events.pop(0)
    
    def get_recent_events(self, n: int = 5, event_type: str = None) -> list:
        """获取最近n条事件，可筛选类型"""
        events = self.events[-n:] if not event_type else [
            e for e in self.events if e["type"] == event_type
        ][-n:]
        return events
    
    def get_event_sentiment(self, event_type: str, hours: float = 48) -> float:
        """
        获取某类事件在最近hours小时内的平均情感影响
        
        Returns:
            float: -1 (负面) ~ 1 (正面)，0 表示无记录
        """
        import time as time_module
        current_time = time_module.time()  # fallback
        # 实际应从外部传入当前时间，这里简化处理
        recent = [e for e in self.events[-50:] if e["type"] == event_type]
        if not recent:
            return 0.0
        return sum(e["impact"] for e in recent) / len(recent)
    
    def record_place(self, pos: tuple, place_type: str, time: float, sentiment: float = 0.0):
        """记录地点记忆"""
        key = pos
        if key in self.places:
            self.places[key]["visits"] += 1
            self.places[key]["last_visit"] = time
            # 情感平均化
            old_sentiment = self.places[key]["sentiment"]
            visits = self.places[key]["visits"]
            self.places[key]["sentiment"] = (old_sentiment * (visits - 1) + sentiment) / visits
        else:
            self.places[key] = {
                "type": place_type,
                "last_visit": time,
                "sentiment": sentiment,
                "visits": 1,
            }
    
    def get_place_sentiment(self, pos: tuple) -> float:
        """获取对某个地点的情感，无记录返回0"""
        key = pos
        if key in self.places:
            return self.places[key]["sentiment"]
        return 0.0
    
    def find_best_place_by_type(self, place_type: str) -> tuple:
        """根据类型找到情感最好的地点位置"""
        candidates = [
            (pos, info) for pos, info in self.places.items()
            if info["type"] == place_type
        ]
        if not candidates:
            return None
        # 按情感排序，返回最好的
        best = max(candidates, key=lambda x: x[1]["sentiment"])
        return best[0]
    
    def record_person(self, entity_id: int, name: str, time: float, 
                      relationship: str = "acquaintance", trust: float = 0.5):
        """记录人物记忆"""
        if entity_id in self.people:
            self.people[entity_id]["last_interaction"] = time
            # 信任度缓慢更新
            old_trust = self.people[entity_id]["trust"]
            self.people[entity_id]["trust"] = old_trust * 0.8 + trust * 0.2
        else:
            self.people[entity_id] = {
                "name": name,
                "relationship": relationship,
                "last_interaction": time,
                "trust": trust,
                "events": [],
            }
    
    def record_success(self, action_type: str):
        """记录成功的行动"""
        if action_type in self.recent_successes:
            self.recent_successes[action_type] += 1
        # 衰减其他行动的成功记录
        for key in self.recent_successes:
            if key != action_type:
                self.recent_successes[key] = max(0, self.recent_successes[key] - 0.5)
