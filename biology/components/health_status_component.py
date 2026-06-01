#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/health_status_component.py
@说明:健康状态组件（统一版）

合并历史（2026-05-31）：
- 原 HealthComponent（hp/max_hp/fatigue/injury）
- 原 DamageComponent（total_damage/wounds/repair_efficiency/max_damage）
-  fatigue 已迁移至 PhysiologyNeedsComponent
-  injury dict 已被结构化 wounds 列表替代
"""

from dataclasses import dataclass, field
from typing import List

from core.component import Component


@dataclass
class WoundRecord:
    """伤口记录"""
    type: str                    # 伤口类型：physical, bleeding, poison, fracture
    severity: float = 0.0        # 严重程度 (0~100)
    age: float = 0.0             # 已存在时间（小时）
    damage_per_sec: float = 0.0  # 每秒持续伤害
    duration: float = -1.0       # 持续时间，-1 表示永久


@dataclass
class HealthStatusComponent(Component):
    """
    健康状态组件（Health + Damage 合并版）

    Attributes:
        hp: 当前生命值
        max_hp: 最大生命值
        total_damage: 总损伤值 (0~100)
        wounds: 伤口列表
        repair_efficiency: 修复效率系数 (0~1)
        max_damage: 最大损伤上限
    """

    # 生命相关（从 HealthComponent 迁入）
    hp: float = 100.0
    max_hp: float = 100.0

    # 损伤相关（从 DamageComponent 迁入）
    total_damage: float = 0.0
    wounds: List[WoundRecord] = field(default_factory=list)
    repair_efficiency: float = 1.0
    max_damage: float = 100.0

    def add_wound(self, wound_type: str, severity: float,
                  damage_per_sec: float = 0.0, duration: float = -1.0):
        """添加新伤口"""
        self.wounds.append(WoundRecord(
            type=wound_type,
            severity=severity,
            age=0.0,
            damage_per_sec=damage_per_sec,
            duration=duration,
        ))
        self.total_damage = min(self.max_damage, self.total_damage + severity)

    def remove_healed_wounds(self, heal_threshold: float = 0.1):
        """移除已愈合的伤口"""
        self.wounds = [w for w in self.wounds if w.severity > heal_threshold]
        self.total_damage = sum(w.severity for w in self.wounds)

    def get_total_severity(self) -> float:
        """获取所有伤口的总严重程度"""
        return sum(w.severity for w in self.wounds)

    def update_wounds(self, dt: float) -> float:
        """更新伤口年龄并计算持续伤害"""
        total_dot = 0.0
        for wound in self.wounds:
            wound.age += dt
            if wound.duration > 0 and wound.age >= wound.duration:
                wound.severity = 0.0
            elif wound.damage_per_sec > 0:
                total_dot += wound.damage_per_sec * dt
        return total_dot
