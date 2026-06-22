#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:perception_filter.py
@说明:感知过滤器

职责：
    - FOV 锥形过滤
    - 视距分层（近/中/远距）
'''

import math
from typing import List

from human.components.perception.vision_component import VisionComponent


class PerceptionFilter:
    """感知过滤器"""

    def filter_by_fov(
        self, observer_x: float, observer_y: float,
        vision: VisionComponent, candidate_ids: list, space_system
    ) -> list:
        """FOV 锥形过滤：只保留位于视野锥形范围内的实体"""
        if vision.fov_angle >= 360.0:
            return candidate_ids

        half_fov = vision.fov_angle / 2.0
        visible = []

        for eid in candidate_ids:
            pos = space_system.get_position(eid)
            if pos is None:
                continue
            ex, ey = pos
            dx, dy = ex - observer_x, ey - observer_y
            if dx == 0 and dy == 0:
                continue
            angle = math.degrees(math.atan2(dy, dx))
            # 计算与中心方向的最小角度差（处理 360° 环绕）
            diff = abs((angle - vision.fov_direction + 180) % 360 - 180)
            if diff <= half_fov:
                visible.append(eid)

        return visible

    def classify_distance(
        self, observer_x: float, observer_y: float,
        vision: VisionComponent, entity_ids: list, space_system
    ) -> dict:
        """
        视距分层：近距清晰、中距模糊、远距仅能感知存在

        Returns:
            {entity_id: distance_tier}，tier = "near" / "mid" / "far"
        """
        tiers = {}
        near_r = vision.radius * 0.3
        mid_r = vision.radius * 0.7

        for eid in entity_ids:
            pos = space_system.get_position(eid)
            if pos is None:
                continue
            dist = math.hypot(pos[0] - observer_x, pos[1] - observer_y)
            if dist <= near_r:
                tiers[eid] = "near"
            elif dist <= mid_r:
                tiers[eid] = "mid"
            else:
                tiers[eid] = "far"

        return tiers
