#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物感知组件

存储动物的感官状态，包括视觉、听觉、嗅觉范围及当前感知到的实体。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from core.component import Component


@dataclass(slots=True)
class AnimalPerceptionComponent(Component):
    """
    动物感知组件

    属性:
        vision_range: 视觉范围
        hearing_range: 听觉范围
        smell_range: 嗅觉范围
        detected_entities: 当前感知到的实体列表 {entity_id: type}
        last_perception_tick: 上次感知更新的 tick
        perception_accuracy: 感知准确度 (0.0~1.0)
        is_night_vision: 是否夜视
    """
    vision_range: float = 10.0
    hearing_range: float = 15.0
    smell_range: float = 8.0
    detected_entities: Dict[int, str] = field(default_factory=dict)
    last_perception_tick: int = 0
    perception_accuracy: float = 0.8
    is_night_vision: bool = False

    def add_detection(self, entity_id: int, entity_type: str) -> None:
        """添加感知到的实体"""
        self.detected_entities[entity_id] = entity_type

    def clear_detection(self) -> None:
        """清空感知列表"""
        self.detected_entities.clear()

    def get_by_type(self, entity_type: str) -> List[int]:
        """获取某类型的所有感知实体"""
        return [eid for eid, etype in self.detected_entities.items() if etype == entity_type]

    def has_detected(self, entity_id: int) -> bool:
        """检查是否感知到某实体"""
        return entity_id in self.detected_entities
