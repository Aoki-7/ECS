#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
DeathReasonComponent — 死亡原因记录组件

DeathSystem 在执行死亡流程时，将最终的死亡原因（可能合并多个 PendingDeath）
记录到该组件，供后续统计、事件传播、社会影响计算等使用。
"""

from dataclasses import dataclass, field
from typing import List
from core.component import Component


@dataclass
class DeathReasonComponent(Component):
    """
    死亡原因记录。支持记录多个贡献因素。

    Fields:
        primary_reason: 主要死亡原因，如 "starvation"
        all_reasons: 所有参与死亡的 PendingDeath 原因列表
        primary_source: 产生主要死亡原因的业务系统名称
    """
    primary_reason: str = "unknown"
    all_reasons: List[str] = field(default_factory=list)
    primary_source: str = "unknown"