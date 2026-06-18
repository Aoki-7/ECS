#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物领地组件 - 纯数据版

存储动物的领地范围、边界标记和防御状态。
"""

from dataclasses import dataclass, field
from typing import List, Tuple

from core.component import Component


@dataclass(slots=True)
class AnimalTerritoryComponent(Component):
    """
    动物领地组件 - 纯数据

    属性:
        center_x: 领地中心 X
        center_y: 领地中心 Y
        radius: 领地半径
        boundary_markers: 边界标记点列表 [(x, y), ...]
        defense_level: 防御等级 (0.0~1.0)
        intruders: 当前入侵者实体 ID 列表
        last_patrol_time: 上次巡逻时间戳
        scent_strength: 气味标记强度 (0.0~1.0，随时间衰减)
    """
    center_x: float = 0.0
    center_y: float = 0.0
    radius: float = 10.0
    boundary_markers: List[Tuple[float, float]] = field(default_factory=list)
    defense_level: float = 0.5
    intruders: List[int] = field(default_factory=list)
    last_patrol_time: float = 0.0
    scent_strength: float = 1.0
