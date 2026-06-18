#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/immune_component.py
@说明:免疫组件 - 纯数据版

存储生物实体的免疫状态，包括抵抗力、感染状态、免疫记忆。
被 ImmuneSystem 读写，被 DeathSystem 间接影响（感染致死）。
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from core.component import Component


@dataclass(slots=True)
class ImmuneComponent(Component):
    """
    免疫组件 - 纯数据

    Attributes:
        resistance: 基础抵抗力 (0~1)，受基因和健康状况影响。
        infection_status: 当前感染状态，
                          healthy / incubating / infected / recovering / immune。
        pathogen_type: 当前感染的病原体类型标识（如 "fungus", "bacteria", "virus"）。
        infection_duration: 当前感染持续时间（小时）。
        immune_memory: 对特定病原体的免疫记忆，键为病原体类型，值为免疫强度 (0~1)。
        symptom_severity: 症状严重程度 (0~1)，影响能量消耗和光合效率。
        infection_count: 累计感染次数（可用于统计或降低后期抵抗力）。
    """

    resistance: float = 1.0
    infection_status: str = "healthy"
    pathogen_type: Optional[str] = None
    infection_duration: float = 0.0
    immune_memory: Dict[str, float] = field(default_factory=dict)
    symptom_severity: float = 0.0
    infection_count: int = 0

    # 兼容旧系统：属性别名
    @property
    def is_healthy(self) -> bool:
        return self.infection_status == "healthy"

    @property
    def is_contagious(self) -> bool:
        return self.infection_status in ("infected", "incubating")

    @property
    def is_infected(self) -> bool:
        return self.infection_status == "infected"
