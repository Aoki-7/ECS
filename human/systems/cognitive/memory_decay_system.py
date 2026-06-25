#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
MemoryDecaySystem - 记忆衰减系统 v2.0

职责：
- 每 tick 扫描 MemoryComponent
- 按时间衰减事件记忆、地点记忆、人物记忆
- 删除过期/低重要性记忆，防止内存无限增长

修复说明（v2.0）：
    原系统期望 `memory.memories` 属性，但 MemoryComponent 实际使用
    `events`、`places`、`people` 三个独立存储区。本版本修复为直接
    操作这三个实际存在的字段。

衰减规则：
    - events: 按 impact 和 age 衰减，低 impact 的旧事件优先遗忘
    - places: 按 visits 和 last_visit 衰减，很少访问的地点逐渐遗忘
    - people: 按 last_interaction 和 trust 衰减
"""

import logging
from core.system import System
from core.world import World

from human.components.cognitive.memory_component import MemoryComponent

logger = logging.getLogger(__name__)


class MemoryDecaySystem(System):
    tick_interval = 5
    """
    记忆衰减系统 v2.0

    模拟人类记忆的遗忘过程：
    - 近期记忆保留较好
    - 远期记忆逐渐模糊
    - 高重要性/高频访问的记忆衰减更慢
    """

    priority = 45

    def __init__(self):
        super().__init__()
        self.decay_rate = 0.05
        self.event_age_threshold = 48.0    # 超过 48 小时开始显著衰减
        self.place_visit_threshold = 3     # 访问少于 3 次的地点容易遗忘
        self.people_trust_threshold = 0.2  # 信任度低于此值的人物容易遗忘
        self.max_events = 100
        self.max_places = 50
        self.max_people = 30

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)

        for entity, (memory,) in world.get_components(MemoryComponent):
            memory: MemoryComponent

            removed_events = self._decay_events(memory, dt)
            removed_places = self._decay_places(memory, dt)
            removed_people = self._decay_people(memory, dt)

            total_removed = removed_events + removed_places + removed_people
            if total_removed > 0:
                logger.debug(
                    f"[MemoryDecay] E{entity.id}: "
                    f"events_removed={removed_events}, places_removed={removed_places}, "
                    f"people_removed={removed_people}"
                )

    def _decay_events(self, memory: MemoryComponent, dt: float) -> int:
        """衰减事件记忆。低 impact 的旧事件优先删除。返回删除数量。"""
        if not memory.events:
            return 0

        current_time = max(e.get("time", 0) for e in memory.events) if memory.events else 0
        to_remove = []

        for idx, event in enumerate(memory.events):
            impact = event.get("impact", 0.0)
            age = current_time - event.get("time", 0)

            # 衰减公式：高 impact 的记忆衰减更慢
            decay_mult = 1.0 / max(1.0, abs(impact) * 10.0 + 1.0)
            effective_age = age * decay_mult

            if effective_age > self.event_age_threshold:
                to_remove.append(idx)

        # 从后往前删除避免索引错位
        for idx in reversed(to_remove):
            memory.events.pop(idx)

        # 若仍超过上限，删除最旧的低 impact 事件
        excess = len(memory.events) - self.max_events
        if excess > 0:
            # 按 (time 升序, impact 升序) 排序，删除最旧且低 impact 的
            scored = [
                (i, e.get("time", 0), abs(e.get("impact", 0)))
                for i, e in enumerate(memory.events)
            ]
            scored.sort(key=lambda x: (x[1], x[2]))
            for idx, _, _ in scored[:excess]:
                memory.events.pop(idx)
                to_remove.append(idx)

        return len(set(to_remove))

    def _decay_places(self, memory: MemoryComponent, dt: float) -> int:
        """衰减少访问的地点记忆。返回删除数量。"""
        if not memory.places:
            return 0

        current_time = max(p.get("last_visit", 0) for p in memory.places.values()) if memory.places else 0
        to_remove = []

        for pos, place in memory.places.items():
            visits = place.get("visits", 0)
            last_visit = place.get("last_visit", 0)
            age = current_time - last_visit

            # 很少访问且很久没更新的地点 → 遗忘
            if visits < self.place_visit_threshold and age > self.event_age_threshold:
                to_remove.append(pos)

        for pos in list(to_remove):
            memory.places.pop(pos, None)

        # 若仍超过上限，删除 sentiment 最低且 oldest 的地点
        excess = len(memory.places) - self.max_places
        if excess > 0:
            items = [
                (pos, p.get("last_visit", 0), p.get("sentiment", 0))
                for pos, p in list(memory.places.items())
            ]
            items.sort(key=lambda x: (x[1], x[2]))
            for pos, _, _ in items[:excess]:
                memory.places.pop(pos, None)
                to_remove.append(pos)

        return len(set(to_remove))

    def _decay_people(self, memory: MemoryComponent, dt: float) -> int:
        """衰减低信任度的人物记忆。返回删除数量。"""
        if not memory.people:
            return 0

        to_remove = []

        for entity_id, person in list(memory.people.items()):
            trust = person.get("trust", 0.0)
            if trust < self.people_trust_threshold:
                to_remove.append(entity_id)

        for entity_id in list(to_remove):
            memory.people.pop(entity_id, None)

        # 若仍超过上限，删除 trust 最低的人物
        excess = len(memory.people) - self.max_people
        if excess > 0:
            items = [
                (eid, p.get("trust", 0.0))
                for eid, p in list(memory.people.items())
            ]
            items.sort(key=lambda x: x[1])
            for eid, _ in items[:excess]:
                memory.people.pop(eid, None)
                to_remove.append(eid)

        return len(set(to_remove))
