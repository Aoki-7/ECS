#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
DeathEventSystem — 死亡事件传播与社会影响系统

职责：
    1. 扫描新死亡的实体（DeadTagComponent.processed == True 但尚未广播）
    2. 将死亡事件传播给死者的亲属、朋友、部落成员
    3. 更新社会情绪（哀悼、恐慌）
    4. 触发人口统计更新
    5. （预留）遗产继承、职位空缺等社会连锁反应

这是一个纯骨架实现，为后续扩展预留接口。
"""

import logging
from typing import Optional

from core.system import System
from core.world import World

from biology.lifecycle.death.components.dead_tag_component import DeadTagComponent
from biology.lifecycle.death.components.death_reason_component import DeathReasonComponent
from biology.lifecycle.death.components.death_time_component import DeathTimeComponent

logger = logging.getLogger(__name__)


class DeathEventSystem(System):
    tick_interval = 5  # 每 5 帧执行一次，降低开销
    """
    死亡事件传播系统。

    扫描新死亡实体并触发社会影响。
    """

    def update(self, world: World, dt: float = 1.0) -> None:
        for entity, (dead_tag,) in list(world.get_components(DeadTagComponent)):
            if not world.has_entity(entity):
                continue

            if dead_tag.processed:
                # 已处理过，但这里可以检查是否有新的传播需求
                continue

            # 标记为已广播
            dead_tag.processed = True

            reason_comp = world.get_component(entity, DeathReasonComponent)
            time_comp = world.get_component(entity, DeathTimeComponent)

            reason = reason_comp.primary_reason if reason_comp else "unknown"
            death_time = time_comp.world_time_display if time_comp else "unknown"

            # 记录社会影响日志
            logger.info(f"[DeathEvent] E{entity.id} death broadcast: {reason} at {death_time}")

            # 1. 在亲属/朋友的 MemoryComponent 中记录死亡事件
            self._notify_relatives(world, entity, reason, death_time)

            # 2. 更新部落情绪（恐惧、悲伤）
            self._update_tribe_mood(world, entity, reason)

    def _notify_relatives(self, world: World, dead_entity, reason: str, death_time: str) -> None:
        """将死亡事件记录到相关实体的记忆中"""
        try:
            from human.components.cognitive.memory_component import MemoryComponent
            from human.components.social.relationship_component import RelationshipComponent
            from identity.name_component import NameComponent
        except (ImportError, AttributeError):
            return

        dead_name_comp = world.get_component(dead_entity, NameComponent)
        dead_name = dead_name_comp.name if dead_name_comp else f"E{dead_entity.id}"

        for entity, (relation,) in list(world.get_components(RelationshipComponent)):
            if not world.has_entity(entity):
                continue
            if getattr(relation, 'partner_id', None) == dead_entity.id:
                memory = world.get_component(entity, MemoryComponent)
                if memory is not None:
                    memory.add_event(
                        world.get_time().total_hours if world.get_time() else 0.0,
                        "partner_death",
                        f"伴侣 {dead_name} 因 {reason} 去世",
                        impact=-1.0,
                        data={"deceased_id": dead_entity.id, "reason": reason}
                    )

    def _update_tribe_mood(self, world: World, dead_entity, reason: str) -> None:
        """更新部落整体情绪（恐惧、悲伤）"""
        try:
            from human.components.cognitive.emotion_component import EmotionComponent
            from human.components.basic.human_component import HumanComponent
        except (ImportError, AttributeError):
            return

        # 对同部落或附近的人类施加短暂情绪影响
        for entity, (emotion, _) in list(world.get_components(EmotionComponent, HumanComponent)):
            if not world.has_entity(entity) or entity.id == dead_entity.id:
                continue
            # 悲伤 + 恐惧（对非正常死亡）
            emotion.adjust_emotion("sadness", 0.05)
            if reason in ("starvation", "dehydration", "hp_depleted"):
                emotion.adjust_emotion("fear", 0.03)
