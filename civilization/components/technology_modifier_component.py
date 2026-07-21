#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TechnologyModifierComponent — 文明技术全局效果组件

挂载到世界实体，由 TechnologySystem 更新，其他业务系统读取。
用于将抽象的“已解锁技术”转化为具体数值加成，避免系统之间直接耦合。
"""

from dataclasses import dataclass

from core.component import Component
from core.component_serializer import register_component


@register_component
@dataclass(slots=True)
class TechnologyModifierComponent(Component):
    """
    技术全局修正组件

    所有字段默认 1.0，表示无加成；大于 1.0 表示正面加成，
    小于 1.0 表示负面（当前不生效）。
    """
    harvest_multiplier: float = 1.0      # 农业收获产量加成
    gather_multiplier: float = 1.0         # 环境资源采集加成
    healthcare_multiplier: float = 1.0     # 自然恢复与医疗效果加成
    construction_efficiency: float = 1.0 # 建造效率加成

    def to_dict(self) -> dict:
        return {
            "harvest_multiplier": self.harvest_multiplier,
            "gather_multiplier": self.gather_multiplier,
            "healthcare_multiplier": self.healthcare_multiplier,
            "construction_efficiency": self.construction_efficiency,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TechnologyModifierComponent":
        return cls(
            harvest_multiplier=data.get("harvest_multiplier", 1.0),
            gather_multiplier=data.get("gather_multiplier", 1.0),
            healthcare_multiplier=data.get("healthcare_multiplier", 1.0),
            construction_efficiency=data.get("construction_efficiency", 1.0),
        )
