#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物学习组件 — 纯数据版

v3.9 迁移：移除所有业务逻辑方法，迁移到 AnimalLearningSystem。
"""

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component


@dataclass
class BehaviorRecord:
    """单条行为记录"""
    behavior: str  # 行为名称
    context: str   # 上下文
    outcome: float  # 结果评分 (-1.0 ~ 1.0)
    count: int = 1  # 发生次数


@dataclass(slots=True)
class AnimalLearningComponent(Component):
    """
    动物学习组件 — 纯数据

    属性:
        behavior_records: 行为记录列表
        habituation: 习惯化程度 {stimulus: level}
        sensitization: 敏感化标记 {stimulus: level}
        learning_rate: 学习速率
        max_records: 最大记录数
    """
    behavior_records: List[BehaviorRecord] = field(default_factory=list)
    habituation: Dict[str, float] = field(default_factory=dict)
    sensitization: Dict[str, float] = field(default_factory=dict)
    learning_rate: float = 0.1
    max_records: int = 50