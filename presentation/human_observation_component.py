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

    def add_snapshot(self, snapshot: Dict[str, Any]):
        """添加一条快照，超出上限时裁剪旧记录"""
        self.history.append(snapshot)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_latest(self) -> Dict[str, Any] | None:
        """获取最新快照"""
        return self.history[-1] if self.history else None

    def get_human_history(self, entity_id: int) -> List[Dict[str, Any]]:
        """
        获取某个特定 human 的所有历史状态

        Returns:
            按时间排序的状态列表，每项包含 timestamp、step 及该 human 的所有字段
        """
        result = []
        for record in self.history:
            for human in record.get("humans", []):
                if human.get("entity_id") == entity_id:
                    result.append({
                        "timestamp": record.get("timestamp"),
                        "step": record.get("step"),
                        **human
                    })
        return result

    def get_human_count_trend(self) -> List[Dict[str, Any]]:
        """获取人口数量变化趋势"""
        return [
            {
                "timestamp": r.get("timestamp"),
                "step": r.get("step"),
                "count": len(r.get("humans", [])),
            }
            for r in self.history
        ]
