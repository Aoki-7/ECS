#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:physiology_needs_component.py
@说明:生理需求组件
@时间:2026/03/21 21:28:32
@作者:Sherry
@版本:1.0
'''




from dataclasses import dataclass

from core.component import Component


def clamp(value: float, min_v: float, max_v: float) -> float:
    # 限制浮点数位数
    value = round(value, 2)
    return max(min_v, min(value, max_v))


@dataclass
class PhysiologyNeedsComponent(Component):
    """
    生理需求组件（带上下限约束）

    所有数值范围统一为 [0, max_value]
    """

    # ===== 当前值 =====
    hunger: float = 0.0
    thirst: float = 0.0
    energy: float = 70.0
    fatigue: float = 0.0
    social: float = 50.0
    comfort: float = 50.0

    # ===== 最大值 =====
    max_hunger: float = 100.0
    max_thirst: float = 100.0
    max_energy: float = 100.0
    max_fatigue: float = 100.0
    max_social: float = 100.0
    max_comfort: float = 100.0

    # ===== 初始化校正 =====
    def __post_init__(self):
        self._clamp_all()

    # ===== 内部方法 =====
    def _clamp_all(self):
        self.hunger = clamp(self.hunger, 0.0, self.max_hunger)
        self.thirst = clamp(self.thirst, 0.0, self.max_thirst)
        self.energy = clamp(self.energy, 0.0, self.max_energy)
        self.fatigue = clamp(self.fatigue, 0.0, self.max_fatigue)
        self.social = clamp(self.social, 0.0, self.max_social)
        self.comfort = clamp(self.comfort, 0.0, self.max_comfort)

    # ===== 对外接口（推荐统一使用） =====

    def add_hunger(self, value: float):
        self.hunger = clamp(self.hunger + value, 0.0, self.max_hunger)

    def add_thirst(self, value: float):
        self.thirst = clamp(self.thirst + value, 0.0, self.max_thirst)

    def add_energy(self, value: float):
        self.energy = clamp(self.energy + value, 0.0, self.max_energy)

    def add_fatigue(self, value: float):
        self.fatigue = clamp(self.fatigue + value, 0.0, self.max_fatigue)

    def add_social(self, value: float):
        self.social = clamp(self.social + value, 0.0, self.max_social)

    def add_comfort(self, value: float):
        self.comfort = clamp(self.comfort + value, 0.0, self.max_comfort)