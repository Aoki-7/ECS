#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:disease_component.py
@说明:疾病组件 - 纯数据版

疾病状态：
- infection_type: 感染类型（bacterial/viral/parasitic/fungal）
- severity: 严重程度 [0.0, 1.0]
- contagiousness: 传染性 [0.0, 1.0]
- stage: 疾病阶段（incubation/active/recovery/terminal）
- symptoms: 症状列表
- duration: 已持续时间（tick）
- max_duration: 最大持续时间（tick）
'''

from dataclasses import dataclass, field
from typing import List

from core.component import Component


@dataclass(slots=True)
class DiseaseComponent(Component):
    """
    疾病组件 - 纯数据版

    Attributes:
        disease_name: 疾病名称
        infection_type: 感染类型（bacterial/viral/parasitic/fungal）
        severity: 严重程度 [0.0, 1.0]
        contagiousness: 传染性 [0.0, 1.0]
        stage: 疾病阶段（incubation/active/recovery/terminal）
        symptoms: 症状列表
        duration: 已持续时间（tick）
        max_duration: 最大持续时间（tick）
        is_terminal: 是否致命
    """
    disease_name: str = "unknown"
    infection_type: str = "bacterial"
    severity: float = 0.0
    contagiousness: float = 0.0
    stage: str = "incubation"
    symptoms: List[str] = field(default_factory=list)
    duration: int = 0
    max_duration: int = 100
    is_terminal: bool = False

    def __post_init__(self):
        # 限制数值范围
        self.severity = max(0.0, min(1.0, self.severity))
        self.contagiousness = max(0.0, min(1.0, self.contagiousness))
        self.duration = max(0, self.duration)
        self.max_duration = max(1, self.max_duration)
