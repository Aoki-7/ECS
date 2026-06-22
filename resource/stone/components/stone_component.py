#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:stone_component.py
@说明:石头组件
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Dict

from core.component import Component
from resource.components.base_resource_component import BaseResourceComponent


@dataclass
class StoneComponent(BaseResourceComponent):
    """
    石头组件（可被采集的资源）

    ===== 核心设计 =====
    - 支持多次采集
    - 主要用于建造和工具
    - 支持硬度和类型
    - 支持风化
    """

    # ===== 基础消耗 =====
    harvest_size: float = 0.2    # 每次采集多少

    # ===== 材料属性 =====
    hardness: float = 0.8        # 硬度 [0,1]，影响加工难度
    density: float = 2.5         # 密度（影响重量）
    type: str = "granite"        # 石头类型（花岗岩、砂岩等）

    # ===== 状态属性 =====
    weathering: float = 0.0      # 风化程度 [0,1]
    weathering_rate: float = 0.001  # 风化速度（每tick）

    # ===== 风险属性 =====
    fracture: float = 0.0        # 裂纹程度（>0 会降低强度）
    contamination: float = 0.0   # 污染程度（环境影响）

    # ===== 扩展效果（通用机制）=====
    effects: Dict[str, float] = field(default_factory=dict)
    # 例如：
    # {
    #   "build_strength": 0.9,
    #   "tool_durability": 0.8
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

    def update_weather(self, dt: float):
        """
        石头风化更新
        """
        self.weathering += self.weathering_rate * dt
        self.weathering = min(1.0, self.weathering)

    def get_strength(self) -> float:
        """
        获取强度（考虑风化和裂纹）
        """
        base_strength = 1.0
        weather_penalty = 1.0 - self.weathering * 0.3
        fracture_penalty = 1.0 - self.fracture * 0.5
        return base_strength * weather_penalty * fracture_penalty

    def is_usable(self) -> bool:
        return self.get_strength() > 0.4