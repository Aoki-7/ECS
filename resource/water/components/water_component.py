#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:water_component.py
@说明:水组件
@时间:2026/04/13
@作者:GitHub Copilot
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Dict

from core.component import Component


@dataclass
class WaterComponent(Component):
    """
    水组件（可被饮用的资源）

    ===== 核心设计 =====
    - 支持多次饮用
    - 主要影响水分指标
    - 支持污染/纯净度
    - 支持温度影响
    """

    # ===== 基础消耗 =====
    amount: float = 1.0          # 剩余份数（被喝完后销毁）
    max_amount: float = 200.0    # 最大容量
    sip_size: float = 5.0        # 每次喝掉多少（增加消耗速度，避免水源无限积累）

    # ===== 水分属性 =====
    hydration: float = 50.0      # 水分值（核心）
    temperature: float = 20.0    # 温度（摄氏度）
    purity: float = 1.0          # 纯净度 [0,1]，影响健康

    # ===== 状态属性 =====
    freshness: float = 1.0       # 新鲜度 [0,1]
    evaporation_rate: float = 0.005  # 蒸发速度（每tick）

    is_evaporable: bool = True   # 是否会蒸发

    # ===== 风险属性 =====
    contamination: float = 0.0   # 污染程度（环境影响）
    bacteria: float = 0.0        # 细菌含量（>0 会扣健康）

    # ===== 扩展效果（通用机制）=====
    effects: Dict[str, float] = field(default_factory=dict)
    # 例如：
    # {
    #   "health": -10,  # 污染水会扣健康
    #   "energy": +5    # 凉水可能提神
    # }