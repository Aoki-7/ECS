#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@文件:wood_component.py
@说明:木材组件
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.1
'''

from dataclasses import dataclass, field
from typing import Dict

from resource.components.base_resource_component import BaseResourceComponent


@dataclass
class WoodComponent(BaseResourceComponent):
    """
    木材组件（可被采集的资源）

    ===== 核心设计 =====
    - 支持多次采集
    - 主要用于建造和燃料
    - 支持干燥/潮湿度
    - 支持燃烧属性
    """

    # ===== 基础消耗 =====
    harvest_size: float = 0.25   # 每次采集多少

    # ===== 材料属性 =====
    density: float = 0.5         # 密度（影响重量和强度）
    hardness: float = 0.7        # 硬度（影响加工难度）

    # ===== 状态属性 =====
    moisture: float = 0.3        # 湿度 [0,1]，影响燃烧和保存
    decay_rate: float = 0.005    # 腐朽速度（每tick）

    is_perishable: bool = True   # 是否会腐朽

    # ===== 风险属性 =====
    infestation: float = 0.0     # 虫害程度（>0 会加速腐朽）
    contamination: float = 0.0   # 污染程度（环境影响）

    # ===== 扩展效果（通用机制）=====
    effects: Dict[str, float] = field(default_factory=dict)
    # 例如：
    # {
    #   "fuel_value": 100.0,
    #   "build_quality": 0.8
    # }
