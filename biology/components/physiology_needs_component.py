#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:physiology_needs_component.py
@说明:生理需求组件
@时间:2026/03/21 21:28:32
@作者:Sherry
@版本:1.0
'''




# 已从 human/components/physiological/physiology_needs_component.py 迁移至此
# 向后兼容导入: from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from dataclasses import dataclass

from core.component import Component


def clamp(value: float, min_v: float, max_v: float) -> float:
    # 限制浮点数位数
    value = round(value, 2)
    return max(min_v, min(value, max_v))


@dataclass(slots=True)
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

    # ===== 温度相关（从 TemperatureComponent 迁入）=====
    body_temperature: float = 37.0      # 核心体温 °C
    heat_stress: float = 0.0            # 热应激 0-100
    cold_stress: float = 0.0            # 冷应激 0-100
    is_heatstroke: bool = False
    is_frostbite: bool = False

    # ===== 最大值 =====
    max_hunger: float = 100.0
    max_thirst: float = 100.0
    max_energy: float = 100.0
    max_fatigue: float = 100.0
    max_social: float = 100.0
    max_comfort: float = 100.0
    max_heat_stress: float = 100.0
    max_cold_stress: float = 100.0

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
        self.heat_stress = clamp(self.heat_stress, 0.0, self.max_heat_stress)
        self.cold_stress = clamp(self.cold_stress, 0.0, self.max_cold_stress)

    # ===== 数据校验 =====
    # 所有修改操作应由对应的 System 通过直接修改属性 + _clamp_all() 完成