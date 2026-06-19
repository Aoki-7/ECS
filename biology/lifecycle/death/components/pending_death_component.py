#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
PendingDeathComponent — 待处理死亡标记组件

任何系统（疾病、饥饿、天气、战斗、衰老等）判定某个实体应当死亡时，
不直接删除实体，而是挂载此组件。DeathSystem 统一扫描并执行最终死亡流程。

设计理念：
    - 死亡原因由业务系统产生
    - 死亡执行由 DeathSystem 集中处理
    - 支持多个系统同时标记同一实体（保留所有原因）
"""

from dataclasses import dataclass, field
from typing import Optional
from core.component import Component


@dataclass
class PendingDeathComponent(Component):
    """
    死亡候选标记。挂载此组件表示该实体已被某个系统判定为应死亡。

    Fields:
        reason: 死亡原因标识符，如 "starvation", "disease", "combat",
                "old_age", "hypothermia", "heatstroke", "poison" 等
        source_system: 产生死亡标记的系统名称，便于调试和追溯
        priority: 死亡优先级，用于同一 tick 内多个死亡源的竞争
                  （数值越高越优先，默认 0）
        timestamp: 标记产生时的世界时间（小时），由系统写入
        details: 死亡详情描述，用于日志和事件记录
    """
    reason: str = "unknown"
    source_system: str = "unknown"
    priority: int = 0
    timestamp: float = 0.0
    details: str = ""
