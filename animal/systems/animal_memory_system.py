#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物记忆系统

管理动物的环境记忆：
    1. 记忆衰减：所有记忆随时间自然减弱
    2. 记忆强化：重复访问同一位置增强记忆
    3. 记忆召回：根据当前需求召回相关记忆
    4. 记忆驱动决策：高价值记忆影响行为选择

与 GrazingSystem / PredationSystem 的关系：
    - 觅食成功后在食物位置添加记忆
    - 遭遇捕食者后在威胁位置添加记忆
    - 后续 tick 中优先访问记忆中的高价值位置
"""

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from animal.components.animal_memory_component import AnimalMemoryComponent, MemoryEntry
from space.space_component import SpaceComponent

import logging

logger = logging.getLogger(__name__)


class AnimalMemorySystem(System):
    tick_interval = 10

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新所有动物的记忆"""
        for entity, (animal, memory, space) in world.get_components(
            AnimalComponent, AnimalMemoryComponent, SpaceComponent
        ):
            # 衰减记忆
            AnimalMemorySystem.decay(memory)

            # 检查当前位置是否有已知资源，强化记忆
            self._reinforce_memories(world, entity, memory, space)

            # 清理过期记忆
            self._cleanup_memories(memory)

    # ── 静态工具方法（供外部调用） ──

    @staticmethod
    def add_memory(
        memory: AnimalMemoryComponent,
        x: float,
        y: float,
        memory_type: str,
        entity_id: int = -1,
        value: float = 0.0,
        timestamp: float = 0.0,
    ) -> None:
        """添加新记忆，若容量满则淘汰最弱的记忆"""
        new_entry = MemoryEntry(
            x=x, y=y, entity_id=entity_id,
            memory_type=memory_type, strength=1.0,
            timestamp=timestamp, value=value,
        )
        # 若同位置已有同类型记忆，更新而非新增
        for i, mem in enumerate(memory.memories):
            if mem.memory_type == memory_type and mem.entity_id == entity_id:
                memory.memories[i] = new_entry
                return

        if len(memory.memories) >= memory.max_memories:
            # 淘汰最弱的记忆
            memory.memories.sort(key=lambda m: m.strength)
            memory.memories.pop(0)

        memory.memories.append(new_entry)

    @staticmethod
    def recall_by_type(memory: AnimalMemoryComponent, memory_type: str) -> MemoryEntry | None:
        """按类型回忆最强记忆"""
        candidates = [m for m in memory.memories if m.memory_type == memory_type]
        if not candidates:
            return None
        return max(candidates, key=lambda m: m.strength)

    @staticmethod
    def recall_nearest(
        memory: AnimalMemoryComponent, x: float, y: float, memory_type: str
    ) -> MemoryEntry | None:
        """回忆某类型中距离最近且强度足够的记忆"""
        candidates = [
            m for m in memory.memories
            if m.memory_type == memory_type and m.strength > 0.3
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda m: (m.x - x) ** 2 + (m.y - y) ** 2)

    @staticmethod
    def decay(memory: AnimalMemoryComponent) -> None:
        """衰减所有记忆强度"""
        for mem in memory.memories:
            mem.strength = max(0.0, mem.strength - memory.decay_rate)

    @staticmethod
    def get_memories_by_type(memory: AnimalMemoryComponent, memory_type: str) -> list[MemoryEntry]:
        """获取某类型的所有记忆"""
        return [m for m in memory.memories if m.memory_type == memory_type]

    def _reinforce_memories(
        self, world: World, entity, memory: AnimalMemoryComponent, space: SpaceComponent
    ) -> None:
        """若动物位于记忆中的位置附近，强化该记忆"""
        for mem in memory.memories:
            dist_sq = (mem.x - space.x) ** 2 + (mem.y - space.y) ** 2
            if dist_sq < 4.0:  # 距离 < 2 格
                mem.strength = min(1.0, mem.strength + 0.2)
                mem.timestamp = getattr(world, 'time', 0)

    def _cleanup_memories(self, memory: AnimalMemoryComponent) -> None:
        """清理已遗忘的记忆"""
        before = len(memory.memories)
        memory.memories = [m for m in memory.memories if m.strength > 0.05]
        after = len(memory.memories)
        if before != after and logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[Memory] 清理 {before - after} 条遗忘记忆")
