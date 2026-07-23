#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:physiology_component.py
@说明:生理组件
@时间:2026/03/21 21:39:25
@作者:Sherry
@版本:1.0
'''


from core.component import Component

from dataclasses import dataclass, field

from typing import Dict


"""
使用示例
physiology = PhysiologyComponent(stats={
    "hunger": PhysioStat(
        value=20,
        base_rate=0.08,
        influences={"energy": -0.1}
    ),
    "thirst": PhysioStat(
        value=10,
        base_rate=0.12,
        influences={"energy": -0.2}
    ),
    "energy": PhysioStat(
        value=80,
        base_rate=-0.05,
        influences={}
    )
})
"""


@dataclass
class PhysioStat:
    """
    单个生理指标
    """
    value: float
    min_value: float = 0.0
    max_value: float = 100.0

    # 基础变化速率（每秒）
    base_rate: float = 0.0

    # 耦合项：{其他stat名: 影响系数}
    influences: Dict[str, float] = field(default_factory=dict)



@dataclass
class PhysiologyComponent(Component):
    """
    通用生理组件
    """
    stats: Dict[str, PhysioStat]