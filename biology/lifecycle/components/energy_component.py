#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/energy_component.py
@说明:能量组件

负责存储生物实体的能量状态，包括当前能量值、生长能量池和上限。
被 GrowthSystem、DeathSystem、SenescenceSystem、MorphologySystem 等多个系统读写。
"""

from core.component import Component


class EnergyComponent(Component):
    """
    能量组件

    Attributes:
        value (float): 当前可用能量值。光合收入与呼吸消耗在此增减。
        growth_pool (float): 生长能量池。光合作用盈余中分配给生长的部分，
                             由 MorphologySystem 消耗以更新形态。
        max_energy (float): 能量上限。value 不应超过此值（由外部系统钳制）。
    """

    __slots__ = ("value", "growth_pool", "max_energy")

    def __init__(self, max_energy: float = 100.0):
        self.value: float = 0.0
        self.growth_pool: float = 0.0
        self.max_energy: float = max_energy