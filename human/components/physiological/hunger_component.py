#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:hunger_component.py
@说明:饥饿组件（已废弃）
@时间:2026/03/21 21:28:32
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass
from core.component import Component


@dataclass
class HungerComponent(Component):
    """
    ⚠️ 已废弃的饥饿组件
    
    此组件已被 PhysiologyNeedsComponent 取代。
    请使用 PhysiologyNeedsComponent 来管理所有生理需求，包括饥饿值。
    
    此组件仅为向后兼容而保留，不建议在新代码中使用。
    """
    hunger: float = 0.0  # 饥饿值（0-100），已废弃

    def increase_hunger(self, amount: float):
        """
        增加饥饿值
        
        已废弃：请使用 PhysiologyNeedsComponent.hunger 代替
        """
        self.hunger = min(100.0, self.hunger + amount)

    def decrease_hunger(self, amount: float):
        """
        减少饥饿值
        
        已废弃：请使用 PhysiologyNeedsComponent.hunger 代替
        """
        self.hunger = max(0.0, self.hunger - amount)
