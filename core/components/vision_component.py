#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:vision_component.py
@说明:视野组件 — 人类感知系统的数据载体
@时间:2026/03/28 17:27:08
@作者:Sherry
@版本:2.0

增强说明（v2.0）：
    - 从 360° 圆形雷达升级为锥形 FOV 视野
    - 引入昼夜视觉敏锐度差异
    - 增加注意力机制（人类无法同时关注所有可见物）
    - 新增感知统计字段，供 PerceptionSystem 写入

现实对照：
    - 人类单眼水平视野约 120°，双眼约 180°
    - 夜间视觉（暗视觉）显著下降，依赖杆状细胞
    - 工作记忆容量约 3-4 个对象（注意力机制）
'''

from dataclasses import dataclass, field
from core.component import Component


@dataclass(slots=True)
class VisionComponent(Component):
    """
    视野组件 — 模拟人类视觉感知

    字段分组：
        1) 基础光学参数：radius, fov_angle, fov_direction
        2) 视觉能力：acuity_day, acuity_night
        3) 当前帧感知结果：entities, entity_ids
        4) 注意力机制：attention_capacity, focused_entity_ids, attention_scores
        5) 感知统计：last_perception_tick, entities_seen_this_tick
    """

    # ── 基础光学参数 ──
    radius: int = 12
    """最大视距（格）。人类在开阔地可识别约 100-200m 外的物体，
    在密集环境中降至 10-20m。此处以格子为单位，默认 12 格。"""

    fov_angle: float = 120.0
    """视野角度（度）。默认 120° 对应单眼水平视野，
    正面锥形区域外的实体处于边缘视觉（模糊感知）。"""

    fov_direction: float = 0.0
    """视野朝向（度，0=右/x+）。随实体的移动/行动方向动态更新，
    由 PerceptionSystem 或 MovementSystem 维护。"""

    # ── 视觉能力 ──
    acuity_day: float = 1.0
    """白天视觉敏锐度 (0~1)。1.0 表示清晰识别颜色和细节。"""

    acuity_night: float = 0.2
    """夜晚视觉敏锐度 (0~1)。人类夜间视力显著下降，
    暗视觉主要依赖杆状细胞，无法分辨颜色。"""

    # ── 当前帧感知结果 ──
    entities: list = field(default_factory=list)
    """视野范围内可见的实体对象列表（由 PerceptionSystem 每帧填充）。"""

    entity_ids: list = field(default_factory=list)
    """视野范围内可见的实体 ID 列表（与 entities 一一对应）。"""

    # ── 注意力机制 ──
    attention_capacity: int = 3
    """同时关注的最大目标数。基于人类工作记忆容量
    （Miller's Law: 7±2 项，但视觉注意约 3-4 项），默认 3。"""

    focused_entity_ids: list = field(default_factory=list)
    """当前被注意的目标实体 ID 列表（长度不超过 attention_capacity）。
    由 PerceptionSystem 根据动态性、大小、熟悉度排序后写入。"""

    attention_scores: dict = field(default_factory=dict)
    """每个可见实体的注意力分数字典 {entity_id: score}。
    分数由动态性、大小、熟悉度、威胁等级综合计算。"""

    # ── 感知统计 ──
    last_perception_tick: int = 0
    """上次执行感知的 world tick（用于判断感知是否过期）。"""

    entities_seen_this_tick: int = 0
    """本帧看到的实体数量（用于统计和决策系统参考）。"""
