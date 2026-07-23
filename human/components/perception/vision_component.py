#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
视野组件 — 人类感知系统的数据载体

v3.9 迁移：从 core/components/ 移回 human/components/perception/
保持 core 层纯粹性。
"""

from dataclasses import dataclass, field
from core.component import Component


@dataclass(slots=True)
class VisionComponent(Component):
    """视野组件 — 模拟人类视觉感知"""

    # 基础光学参数
    radius: int = 12
    fov_angle: float = 120.0
    fov_direction: float = 0.0

    # 视觉能力
    acuity_day: float = 1.0
    acuity_night: float = 0.2

    # 当前帧感知结果
    entities: list = field(default_factory=list)
    entity_ids: list = field(default_factory=list)

    # 注意力机制
    attention_capacity: int = 3
    focused_entity_ids: list = field(default_factory=list)
    attention_scores: dict = field(default_factory=dict)

    # 感知统计
    last_perception_tick: int = 0
    entities_seen_this_tick: int = 0