#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@文件:metal_component.py
@说明:金属组件
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.1
'''

from dataclasses import dataclass, field
from typing import Dict

from resource.components.base_resource_component import BaseResourceComponent


@dataclass
class MetalComponent(BaseResourceComponent):
    """
    金属组件（可被采集的资源）

    ===== 核心设计 =====
    - 支持多次采集
    - 主要用于工具和武器
    - 支持熔点和导电性
    - 支持氧化
    """

    # ===== 基础消耗 =====
    harvest_size: float = 0.15   # 每次采集多少

    # ===== 材料属性 =====
    type: str = "iron"           # 金属类型（铁、铜、金等）
    purity: float = 0.9          # 纯度 [0,1]
    conductivity: float = 0.6    # 导电性
    melting_point: float = 1500.0  # 熔点（摄氏度）

    # ===== 状态属性 =====
    oxidation: float = 0.0       # 氧化程度 [0,1]
    oxidation_rate: float = 0.002  # 氧化速度（每tick）

    # ===== 风险属性 =====
    corrosion: float = 0.0       # 腐蚀程度（>0 会降低强度）
    contamination: float = 0.0   # 污染程度（环境影响）

    # ===== 扩展效果（通用机制）=====
    effects: Dict[str, float] = field(default_factory=dict)
    # 例如：
    # {
    #   "weapon_sharpness": 0.9,
    #   "tool_durability": 0.95
    # }