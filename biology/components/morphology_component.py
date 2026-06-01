#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/morphology_component.py
@说明:形态组件

负责存储生物实体的可视外观与形态参数。
由 MorphologySystem 根据生长池能量和基因分配策略更新。
"""

from core.component import Component
from dataclasses import dataclass


@dataclass
class MorphologyComponent(Component):
    """
    仅负责最终可视外观与物理形态参数

    Attributes:
        height (float): 高度（cm 或相对单位）
        leaf_size (float): 叶片大小（相对单位）
        leaf_count (int): 叶片数量
        stem_thickness (float): 茎干粗细
        root_depth (float): 根系深度
        green_intensity (float): 绿色强度 (0~2)，用于渲染
        yellowing (float): 枯黄程度 (0~1)
        wilting (float): 枯萎程度 (0~1)
    """

    # ===== 基础结构 =====
    height: float = 0.5
    leaf_size: float = 0.5
    leaf_count: int = 2
    stem_thickness: float = 0.1

    # ===== 根系 =====
    root_depth: float = 0.5

    # ===== 颜色 =====
    green_intensity: float = 1.0   # 0~2
    yellowing: float = 0.0         # 0~1 枯黄

    # ===== 状态 =====
    wilting: float = 0.0           # 0~1

    # ===== 身体属性（从 BodyComponent 迁入，人类/动物专属）=====
    weight: float = 0.0            # 体重 / 生物量
    strength: float = 0.0          # 力量
    agility: float = 0.0           # 敏捷
    endurance: float = 0.0         # 耐力

    # ===== 竞争参数（从 CompetitionComponent 迁入）=====
    canopy_radius: float = 1.0
    root_radius: float = 1.0
    competitive_ability: float = 1.0
    light_competition_score: float = 0.0
    water_competition_score: float = 0.0
