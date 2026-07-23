#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:disease_component.py
@说明:疾病组件 - 统一入口（转发到v4版本）
@时间:2026/07/20
@版本:4.0

注意：此文件现在重定向到 disease_component_v4.py，以实现版本统一。
新版 DiseaseManagerComponent 提供完整的旧版 DiseaseComponent 字段兼容
（disease_name, infection_type, severity, contagiousness, stage, symptoms,
duration, max_duration, is_terminal 等）。
'''

from human.components.health.disease_component_v4 import (
    DiseaseManagerComponent,
    Disease,
    DiseaseSeverity,
    DiseaseStage,
    DiseaseType,
    TransmissionMode,
    Epidemic,
)

# 为旧版导入提供兼容别名
DiseaseComponent = DiseaseManagerComponent

__all__ = [
    "DiseaseComponent",
    "DiseaseManagerComponent",
    "Disease",
    "DiseaseSeverity",
    "DiseaseStage",
    "DiseaseType",
    "TransmissionMode",
    "Epidemic",
]