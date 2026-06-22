#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:metal_component.py
@说明:金属组件
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Dict

from core.component import Component
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

    # ===== 行为方法 =====
    def harvest(self) -> float:
        """
        被采集，返回实际采集量
        """
        if self.amount <= 0:
            return 0.0

        harvested = min(self.harvest_size, self.amount)
        self.amount -= harvested
        return harvested

    def is_empty(self) -> bool:
        return self.amount <= 0

    def update_oxidation(self, dt: float):
        """
        金属氧化更新
        """
        self.oxidation += self.oxidation_rate * dt
        self.oxidation = min(1.0, self.oxidation)

    def get_durability(self) -> float:
        """
        获取耐久性（考虑氧化和腐蚀）
        """
        base_durability = 1.0
        oxidation_penalty = 1.0 - self.oxidation * 0.4
        corrosion_penalty = 1.0 - self.corrosion * 0.6
        purity_bonus = self.purity
        return base_durability * oxidation_penalty * corrosion_penalty * purity_bonus

    def is_usable(self) -> bool:
        return self.get_durability() > 0.5