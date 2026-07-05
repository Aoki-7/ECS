#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
人类观察组件

存储所有人类实体的历史状态快照，供观察/回溯使用。
挂在 WorldEntity 上。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any

from core.component import Component


@dataclass
class HumanObservationComponent(Component):
    """
    人类观察组件

    存储所有 human 的状态快照历史，支持按实体回溯。

    Attributes:
        history: 状态快照列表，每项结构为 {
            "timestamp": float,      # 世界总小时数
            "step": int,             # 模拟步数
            "humans": [              # 该时刻所有 human 状态
                {
                    "entity_id": int,
                    "name": str,
                    "age": float,
                    "gender": str,
                    "position": (x, y),
                    "hp": float,
                    "max_hp": float,
                    "hunger": float,
                    "thirst": float,
                    "energy": float,
                    "fatigue": float,
                    "body_temperature": float,
                    "heat_stress": float,
                    "cold_stress": float,
                    "emotion": str,
                    "mood_score": float,
                    "intent": str,
                    "action": str,
                    "diseases": list,   # [{"name": str, "severity": float}]
                    "tribe": str,
                }
            ]
        }
        max_history: 最大保留历史条数，超限时自动裁剪
    """

    history: List[Dict[str, Any]] = field(default_factory=list)
    max_history: int = 500
