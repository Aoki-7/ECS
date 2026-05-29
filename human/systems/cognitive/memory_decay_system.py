#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
MemoryDecaySystem - 记忆衰减系统

职责：
- 每 tick 扫描 MemoryComponent
- 按时间衰减记忆重要性
- 低于阈值的记忆自动删除，防止内存无限增长
"""

import logging
from core.system import System
from core.world import World

from human.components.cognitive.memory_component import MemoryComponent

logger = logging.getLogger(__name__)


class MemoryDecaySystem(System):
    """
    记忆衰减系统

    模拟人类记忆的遗忘过程：
    - 近期记忆保留较好
    - 远期记忆逐渐模糊
    - 重要性高的记忆衰减更慢
    """

    priority = 45  # 在人类核心系统之后，生物学系统之前

    def __init__(self):
        super().__init__()
        self.decay_rate = 0.05       # 基础衰减率 /小时
        self.importance_threshold = 5.0  # 低于此值的记忆删除
        self.max_memories = 200      # 单个实体最大记忆数

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)

        for entity, (memory,) in world.get_components(MemoryComponent):
            memory: MemoryComponent

            if not hasattr(memory, 'memories') or not memory.memories:
                continue

            # 按时间衰减重要性
            to_remove = []
            for idx, mem in enumerate(memory.memories):
                if not isinstance(mem, dict):
                    continue

                importance = mem.get('importance', 50.0)
                age_hours = mem.get('age_hours', 0.0)

                # 重要性衰减：高重要性记忆衰减更慢
                decay_mult = 1.0 / max(1.0, importance / 20.0)
                new_importance = importance - (self.decay_rate * decay_mult * dt)
                mem['importance'] = new_importance
                mem['age_hours'] = age_hours + dt

                # 标记删除
                if new_importance < self.importance_threshold:
                    to_remove.append(idx)

            # 删除低重要性记忆（从后往前删，避免索引错位）
            for idx in reversed(to_remove):
                memory.memories.pop(idx)

            # 若记忆数仍超过上限，删除最旧的低重要性记忆
            excess = len(memory.memories) - self.max_memories
            if excess > 0:
                # 按 (importance, age) 排序，删除综合评分最低的
                scored = [
                    (i, m.get('importance', 0) - m.get('age_hours', 0) * 0.01)
                    for i, m in enumerate(memory.memories)
                ]
                scored.sort(key=lambda x: x[1])
                for idx, _ in scored[:excess]:
                    memory.memories.pop(idx)

            logger.debug(
                f"[MemoryDecay] E{entity.id}: "
                f"removed={len(to_remove)}, remaining={len(memory.memories)}"
            )
