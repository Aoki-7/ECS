#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@文件:food_component.py
@说明:食物组件
@时间:2026/03/18 15:16:09
@作者:Sherry
@版本:1.1
'''

from dataclasses import dataclass, field
from typing import Dict

from resource.components.base_resource_component import BaseResourceComponent


@dataclass
class FoodComponent(BaseResourceComponent):
    """
    食物组件（可被消费的资源）

    ===== 核心设计 =====
    - 支持多次食用
    - 同时影响多个生理指标（不仅仅是饱腹）
    - 支持腐败 / 新鲜度
    - 支持负面效果（中毒等）
    """

    # ===== 基础消耗 =====
    bite_size: float = 0.25      # 每次吃掉多少

    # ===== 营养属性 =====
    nutrition: float = 30.0      # 饱腹值（核心）
    hydration: float = 0.0       # 水分（影响口渴）
    energy: float = 10.0         # 能量（影响体力）
    health: float = 0.0          # 健康影响（正/负）

    # ===== 状态属性 =====
    freshness: float = 1.0       # 新鲜度 [0,1]
    decay_rate: float = 0.0005   # 腐败速度（每tick），2000步后才触发腐败

    is_perishable: bool = True   # 是否会腐败

    # ===== 风险属性 =====
    poison: float = 0.0          # 毒性（>0 会扣健康）
    contamination: float = 0.0   # 污染程度（环境影响）

    # ===== 扩展效果（通用机制）=====
    effects: Dict[str, float] = field(default_factory=dict)
    # 例如：
    # {
    #   "mood": +5,
    #   "stress": -3
    # }