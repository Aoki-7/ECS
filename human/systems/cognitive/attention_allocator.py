#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:attention_allocator.py
@说明:注意力分配器

职责：
    - 为每个可见实体计算注意力分数
    - 返回前 N 个最高分的实体

评分维度：
    - 动态性 (+0.3)：有 VelocityComponent 的实体更容易吸引注意
    - 大小 (+0.2)：MorphologyComponent.weight 越大越显眼
    - 熟悉度 (+0.2)：在记忆中的人更容易被注意
    - 异常 (+0.1)：尸体、死亡标记
    - 距离 (+0.2)：近距离加分
'''

import math
from typing import Dict, List, Tuple, Optional

from core.world import World
from human.components.perception.vision_component import VisionComponent
from human.components.cognitive.memory_component import MemoryComponent


class AttentionAllocator:
    """注意力分配器"""

    def allocate_attention(
        self, world: World, observer, observer_x: float, observer_y: float,
        vision: VisionComponent, visible_ids: list, memory: Optional[MemoryComponent]
    ) -> Tuple[list, dict]:
        """
        注意力分配：为每个可见实体计算注意力分数，返回前 N 个。

        Returns:
            (focused_ids, scores)
        """
        scores = {}

        for eid in visible_ids:
            target = world.query_entity(eid)
            if target is None:
                continue

            score = 0.0
            t_space = world.get_component(target, 'SpaceComponent')
            dist = math.hypot(t_space.x - observer_x, t_space.y - observer_y) if t_space else vision.radius
            norm_dist = 1.0 - min(1.0, dist / max(1.0, vision.radius))

            # 近距离加分
            score += norm_dist * 0.2

            # 动态性加分
            from human.components.abilities.velocity_component import VelocityComponent
            if world.get_component(target, VelocityComponent) is not None:
                score += 0.3

            # 大小加分
            from biology.lifecycle.components.morphology_component import MorphologyComponent
            morph = world.get_component(target, MorphologyComponent)
            if morph is not None and morph.weight > 0:
                score += min(0.2, morph.weight / 100.0)

            # 熟悉度加分
            if memory is not None:
                if eid in getattr(memory, 'people', {}):
                    score += 0.2

            # 异常加分（尸体、死亡标记）
            from biology.lifecycle.death.components.dead_tag_component import DeadTagComponent
            if world.get_component(target, DeadTagComponent) is not None:
                score += 0.1

            scores[eid] = round(score, 3)

        # 取前 N 个最高分
        sorted_ids = sorted(scores.keys(), key=lambda eid: scores[eid], reverse=True)
        focused = sorted_ids[:vision.attention_capacity]
        return focused, scores
