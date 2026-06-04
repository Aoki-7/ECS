#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
物种形成追踪组件

记录实体的物种谱系信息，用于物种形成系统计算遗传距离和识别新物种。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass(slots=True)
class SpeciationTrackerComponent(Component):
    """
    物种形成追踪组件

    Attributes:
        species_id: 当前物种标识符（如 "herbivore", "herbivore_variant_a"）
        original_species: 原始祖先物种标识符（追溯用）
        generation: 自该血统分支以来的代数
        lineage_id: 血统链 ID，格式为 "原始物种_随机后缀"
    """
    species_id: str = "unknown"
    original_species: str = "unknown"
    generation: int = 0
    lineage_id: str = ""
