#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
CorpseComponent — 尸体组件

DeathSystem 完成死亡流程后，CorpseSystem 将尸体实体保留在世界中一段时间，
用于腐败、分解、被食腐动物利用、传染病传播等后续逻辑。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass
class CorpseComponent(Component):
    """
    尸体标记组件。

    Fields:
        original_entity_id: 死亡前实体的 ID（用于追溯）
        original_name: 死亡前实体的名称
        decay_progress: 腐败进度 [0.0, 1.0]，达到 1.0 时尸体完全分解
        decay_rate: 腐败速率（每小时），受温度/湿度影响
        is_looted: 是否已被搜刮过（防止重复搜刮）
        original_type: 原始实体类型，如 "human", "animal", "plant"
    """
    original_entity_id: int = 0
    original_name: str = ""
    decay_progress: float = 0.0
    decay_rate: float = 0.01  # 默认 1%/小时
    is_looted: bool = False
    original_type: str = "unknown"