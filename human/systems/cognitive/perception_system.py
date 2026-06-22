#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:perception_system.py
@说明:感知系统 — 从 360° 雷达升级为锥形 FOV + 注意力 + 记忆写入
@时间:2026/03/28 17:30:09
@作者:Sherry / AI Assistant
@版本:3.0

增强说明（v3.0）：
    1. FOV 锥形过滤：只保留 fov_direction ± fov_angle/2 范围内的实体
    2. 注意力分配：按动态性、大小、熟悉度计算注意力分数，只关注前 N 个
    3. 视距分层：近距清晰、中距模糊、远距仅能感知存在
    4. 记忆写入：看到人 → record_person；看到资源 → record_place；
       看到异常（尸体/敌人）→ add_event("perception_alert")
    
    v3.0 拆分：
    - 感知过滤 -> PerceptionFilter
    - 注意力分配 -> AttentionAllocator
    - 记忆写入 -> MemoryWriter
'''

import math
import logging

from core.system import System
from core.world import World

from space.space_system import SpaceSystem
from human.components.perception.vision_component import VisionComponent
from space.space_component import SpaceComponent
from human.components.cognitive.memory_component import MemoryComponent

from human.systems.cognitive.perception_filter import PerceptionFilter
from human.systems.cognitive.attention_allocator import AttentionAllocator
from human.systems.cognitive.memory_writer import MemoryWriter

logger = logging.getLogger(__name__)


class PerceptionSystem(System):
    tick_interval = 1
    """
    感知系统 v3.0

    执行流程：
        1. 空间查询：获取 radius 内所有实体
        2. FOV 过滤：只保留锥形视野内的实体（PerceptionFilter）
        3. 视距分层：近/中/远距赋予不同识别精度
        4. 注意力排序：按动态性、大小、熟悉度打分（AttentionAllocator）
        5. 记忆写入：将观察到的人/地点/异常写入 MemoryComponent（MemoryWriter）
    """

    def __init__(self):
        super().__init__()
        self._filter = PerceptionFilter()
        self._allocator = AttentionAllocator()
        self._writer = MemoryWriter()

    def update(self, world: World, dt: float):
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (space, vision) in world.get_components(SpaceComponent, VisionComponent):
            space: SpaceComponent
            vision: VisionComponent

            # 更新视野朝向
            self._update_fov_direction(space, vision)

            x, y = space.x, space.y
            r = vision.radius

            # 1) 空间查询：获取 radius 内所有实体
            id_list = space_system.query_radius(x=x, y=y, r=r)
            candidate_ids = [eid for eid in id_list if eid != entity.id]

            # 2) FOV 锥形过滤
            visible_ids = self._filter.filter_by_fov(x, y, vision, candidate_ids, space_system)

            # 3) 视距分层 + 4) 注意力排序
            memory = world.get_component(entity, MemoryComponent)
            focused_ids, attention_scores = self._allocator.allocate_attention(
                world, entity, x, y, vision, visible_ids, memory
            )

            # 写入 VisionComponent
            vision.entity_ids = visible_ids
            vision.entities = [world.query_entity(eid) for eid in visible_ids]
            vision.focused_entity_ids = focused_ids
            vision.attention_scores = attention_scores
            vision.entities_seen_this_tick = len(visible_ids)
            vision.last_perception_tick = world.tick_count

            # 5) 记忆写入
            if memory is not None:
                self._writer.write_to_memory(world, entity, x, y, vision, visible_ids, memory)

    def _update_fov_direction(self, space: SpaceComponent, vision: VisionComponent):
        """根据实体的 dirty 标志或速度更新视野朝向。当前简化为保持原值，
        若后续接入 VelocityComponent，可改为 velocity 方向。"""
        # 预留：若 VelocityComponent 存在，可读取速度方向更新 fov_direction
        pass


# 向后兼容的旧拼写别名
PreceptionSystem = PerceptionSystem
