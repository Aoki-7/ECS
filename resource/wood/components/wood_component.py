#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:wood_component.py
@说明:木材组件
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Dict

from core.component import Component


@dataclass
class WoodComponent(Component):
    """
    木材组件（可被采集的资源）

    ===== 核心设计 =====
    - 支持多次采集
    - 主要用于建造和燃料
    - 支持干燥/潮湿度
    - 支持燃烧属性
    """

    # ===== 基础消耗 =====
    amount: float = 1.0          # 剩余份数（被采集完后销毁）
    harvest_size: float = 0.25   # 每次采集多少

    # ===== 材料属性 =====
    quality: float = 1.0         # 质量 [0,1]，影响用途
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

    def update_decay(self, dt: float):
        """
        木材腐朽更新
        """
        if not self.is_perishable:
            return

        self.quality -= self.decay_rate * dt * (1 + self.infestation)
        self.quality = max(0.0, self.quality)

    def get_fuel_value(self) -> float:
        """
        获取燃料价值（考虑湿度）
        """
        base_value = 100.0
        moisture_penalty = 1.0 - self.moisture * 0.5
        return base_value * self.quality * moisture_penalty

    def is_usable(self) -> bool:
        return self.quality > 0.3