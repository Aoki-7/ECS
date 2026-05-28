#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/damage_component.py
@说明:损伤组件

记录生物实体受到的物理损伤和伤口状态。
被 DamageRepairSystem 消耗能量修复，被 SenescenceSystem / DeathSystem 间接影响。
"""

from dataclasses import dataclass, field
from typing import List, Dict

from core.component import Component


@dataclass
class DamageComponent(Component):
    """
    损伤组件

    Attributes:
        total_damage: 总损伤值 (0~100)。
        wounds: 伤口列表，每个伤口为字典 {"type": str, "severity": float, "age": float}。
        repair_efficiency: 修复效率系数 (0~1)，受营养和基因影响。
        max_damage: 最大损伤上限。
    """

    total_damage: float = 0.0
    wounds: List[Dict] = field(default_factory=list)
    repair_efficiency: float = 1.0
    max_damage: float = 100.0

    def add_wound(self, wound_type: str, severity: float):
        """
        添加新伤口

        Args:
            wound_type: 伤口类型，如 "physical", "fire", "pest" 等。
            severity: 严重程度 (0~100)。
        """
        self.wounds.append({
            "type": wound_type,
            "severity": severity,
            "age": 0.0,
        })
        self.total_damage = min(self.max_damage, self.total_damage + severity)

    def remove_healed_wounds(self, heal_threshold: float = 0.1):
        """移除已愈合的伤口（severity <= threshold）"""
        self.wounds = [w for w in self.wounds if w["severity"] > heal_threshold]
        self.total_damage = sum(w["severity"] for w in self.wounds)
