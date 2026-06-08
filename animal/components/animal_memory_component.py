#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物记忆组件

存储动物对环境的记忆，包括食物源、水源、威胁、配偶位置等。
记忆会随时间衰减，可被新信息覆盖。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.component import Component


@dataclass
class MemoryEntry:
    """单条记忆条目"""
    x: float
    y: float
    entity_id: int = -1
    memory_type: str = "unknown"  # food, water, threat, mate, shelter
    strength: float = 1.0  # 0.0~1.0，记忆强度
    timestamp: float = 0.0  # 世界时间戳
    value: float = 0.0  # 记忆价值（如食物产量、威胁等级）


@dataclass(slots=True)
class AnimalMemoryComponent(Component):
    """
    动物记忆组件

    属性:
        memories: 记忆列表（按时间排序）
        max_memories: 最大记忆容量
        decay_rate: 记忆衰减率 (每 tick)
        recall_accuracy: 回忆准确度 (0.0~1.0)
    """
    memories: List[MemoryEntry] = field(default_factory=list)
    max_memories: int = 20
    decay_rate: float = 0.01
    recall_accuracy: float = 0.8

    def add_memory(
        self,
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
        for i, mem in enumerate(self.memories):
            if mem.memory_type == memory_type and mem.entity_id == entity_id:
                self.memories[i] = new_entry
                return

        if len(self.memories) >= self.max_memories:
            # 淘汰最弱的记忆
            self.memories.sort(key=lambda m: m.strength)
            self.memories.pop(0)

        self.memories.append(new_entry)

    def recall_by_type(self, memory_type: str) -> Optional[MemoryEntry]:
        """按类型回忆最强记忆"""
        candidates = [m for m in self.memories if m.memory_type == memory_type]
        if not candidates:
            return None
        return max(candidates, key=lambda m: m.strength)

    def recall_nearest(
        self, x: float, y: float, memory_type: str
    ) -> Optional[MemoryEntry]:
        """回忆某类型中距离最近且强度足够的记忆"""
        candidates = [
            m for m in self.memories
            if m.memory_type == memory_type and m.strength > 0.3
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda m: (m.x - x) ** 2 + (m.y - y) ** 2)

    def decay(self) -> None:
        """衰减所有记忆强度"""
        for mem in self.memories:
            mem.strength = max(0.0, mem.strength - self.decay_rate)
        # 清理已遗忘的记忆
        self.memories = [m for m in self.memories if m.strength > 0.05]

    def get_memories_by_type(self, memory_type: str) -> List[MemoryEntry]:
        """获取某类型的所有记忆"""
        return [m for m in self.memories if m.memory_type == memory_type]
