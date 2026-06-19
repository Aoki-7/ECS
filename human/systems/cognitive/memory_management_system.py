#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
MemoryManagementSystem — v4.0 新增

职责：
    - 管理 MemoryComponent 的所有业务逻辑
    - 事件记忆衰减和清理
    - 地点记忆更新
    - 人物关系维护

设计原则：
    - Component 纯数据，System 处理逻辑
    - 静态工具方法供其他 System 调用
'''

import math
from typing import Optional, Tuple, List

from core.system import System
from core.world import World

from human.components.cognitive.memory_component import MemoryComponent


class MemoryManagementSystem(System):
    """记忆管理系统"""

    tick_interval = 10  # 每10帧执行一次

    # 衰减参数
    EVENT_DECAY_RATE = 0.99  # 每帧情感影响衰减
    PLACE_DECAY_RATE = 0.95  # 地点情感衰减
    MAX_SEARCH_DISTANCE = 100.0  # 地点搜索最大距离

    def update(self, world: World, dt: float):
        """更新所有实体的记忆"""
        for entity, (memory,) in world.get_components(MemoryComponent):
            self._decay_events(memory, dt)
            self._decay_places(memory, dt)
            self._limit_history(memory)

    def _decay_events(self, memory: MemoryComponent, dt: float):
        """事件情感衰减"""
        for event in memory.events:
            event['impact'] *= self.EVENT_DECAY_RATE ** dt

    def _decay_places(self, memory: MemoryComponent, dt: float):
        """地点情感衰减"""
        for place_data in memory.places.values():
            place_data['sentiment'] *= self.PLACE_DECAY_RATE ** dt

    def _limit_history(self, memory: MemoryComponent):
        """限制历史记录长度"""
        if len(memory.events) > memory.MAX_EVENTS:
            memory.events = memory.events[-memory.MAX_EVENTS:]

        if len(memory.people) > memory.MAX_PEOPLE:
            # 按最后互动时间排序，保留最近的
            sorted_people = sorted(
                memory.people.items(),
                key=lambda x: x[1].get('last_interaction', 0),
                reverse=True
            )
            memory.people = dict(sorted_people[:memory.MAX_PEOPLE])

    # === 静态工具方法（供其他 System 调用）===

    @staticmethod
    def add_event(memory: MemoryComponent, time: float, event_type: str,
                  description: str, impact: float = 0.0, location: Tuple = None):
        """添加事件记忆"""
        memory.events.append({
            "time": time,
            "type": event_type,
            "description": description,
            "impact": impact,
            "location": location,
        })

    @staticmethod
    def get_recent_events(memory: MemoryComponent, n: int = 5,
                          event_type: str = None) -> List[dict]:
        """获取最近n条事件，可筛选类型"""
        if not event_type:
            return memory.events[-n:]
        filtered = [e for e in memory.events if e["type"] == event_type]
        return filtered[-n:]

    @staticmethod
    def get_event_sentiment(memory: MemoryComponent, event_type: str,
                            current_time: float = None, hours: float = 48) -> float:
        """获取某类事件在最近hours小时内的平均情感影响"""
        if current_time is None:
            relevant = [e for e in memory.events if e["type"] == event_type]
        else:
            relevant = [
                e for e in memory.events
                if e["type"] == event_type and current_time - e["time"] <= hours
            ]

        if not relevant:
            return 0.0

        return sum(e["impact"] for e in relevant) / len(relevant)

    @staticmethod
    def record_place(memory: MemoryComponent, pos: Tuple, place_type: str,
                     time: float, sentiment: float = 0.5):
        """记录地点记忆"""
        key = pos
        if key not in memory.places:
            memory.places[key] = {
                "type": place_type,
                "last_visit": time,
                "sentiment": sentiment,
                "visits": 1,
            }
        else:
            memory.places[key]["last_visit"] = time
            memory.places[key]["visits"] += 1
            # 情感更新（加权平均）
            old_sentiment = memory.places[key]["sentiment"]
            memory.places[key]["sentiment"] = (old_sentiment * 0.7 + sentiment * 0.3)

    @staticmethod
    def find_best_place_by_type(memory: MemoryComponent, place_type: str,
                                current_pos: Tuple) -> Optional[Tuple]:
        """根据类型找到最佳地点（最近 + 情感最好）"""
        candidates = [
            (pos, data) for pos, data in memory.places.items()
            if data["type"] == place_type
        ]

        if not candidates:
            return None

        # 评分 = 情感 - 距离惩罚
        def score(item):
            pos, data = item
            dist = math.hypot(pos[0] - current_pos[0], pos[1] - current_pos[1])
            distance_penalty = dist / MemoryManagementSystem.MAX_SEARCH_DISTANCE
            return data["sentiment"] - distance_penalty

        best = max(candidates, key=score)
        return best[0]

    @staticmethod
    def record_person(memory: MemoryComponent, entity_id: int, name: str,
                      relationship: str, time: float, trust: float = 0.5):
        """记录人物记忆"""
        memory.people[entity_id] = {
            "name": name,
            "relationship": relationship,
            "last_interaction": time,
            "trust": trust,
            "events": [],
        }

    @staticmethod
    def update_relationship(memory: MemoryComponent, entity_id: int,
                            time: float, trust_delta: float = 0.0):
        """更新人物关系"""
        if entity_id not in memory.people:
            return

        person = memory.people[entity_id]
        person["last_interaction"] = time
        person["trust"] = max(0.0, min(1.0, person["trust"] + trust_delta))

    @staticmethod
    def record_success(memory: MemoryComponent, action_type: str):
        """记录成功行动"""
        if action_type in memory.recent_successes:
            memory.recent_successes[action_type] += 1
