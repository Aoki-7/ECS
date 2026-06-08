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
from animal.components.animal_memory_component import AnimalMemoryComponent
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
            memory.decay()

            # 检查当前位置是否有已知资源，强化记忆
            self._reinforce_memories(world, entity, memory, space)

            # 清理过期记忆
            self._cleanup_memories(memory)

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
        if before != after:
            logger.debug(f"[Memory] 清理 {before - after} 条遗忘记忆")
