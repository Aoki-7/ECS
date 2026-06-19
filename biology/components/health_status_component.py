#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/health_status_component.py
@说明:健康状态组件（统一版）— v3.7 纯数据化

合并历史（2026-05-31）：
- 原 HealthComponent（hp/max_hp/fatigue/injury）
- 原 DamageComponent（total_damage/wounds/repair_efficiency/max_damage）
-  fatigue 已迁移至 PhysiologyNeedsComponent
-  injury dict 已被结构化 wounds 列表替代

v3.7 变更：
- 所有业务逻辑迁移到 HealthStatusSystem
- Component 仅保留数据字段
"""

from dataclasses import dataclass, field
from typing import List

from core.component import Component
from core.component_serializer import register_component


@dataclass
class WoundRecord:
    """伤口记录"""
    type: str                    # 伤口类型：physical, bleeding, poison, fracture
    severity: float = 0.0        # 严重程度 (0~100)
    age: float = 0.0             # 已存在时间（小时）
    damage_per_sec: float = 0.0  # 每秒持续伤害
    duration: float = -1.0       # 持续时间，-1 表示永久


@register_component
@dataclass(slots=True)
class HealthStatusComponent(Component):
    """
    健康状态组件（Health + Damage 合并版）— 纯数据

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
