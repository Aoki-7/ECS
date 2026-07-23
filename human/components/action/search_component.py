#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
搜索组件 — 智能目标发现与策略管理

v3.9 迁移：从 core/components/ 移回 human/components/action/
保持 core 层纯粹性。
"""

from dataclasses import dataclass, field
from core.component import Component
from core.component_serializer import ComponentSerializer
from typing import Optional, Type
import importlib


@dataclass(slots=True)
class SearchComponent(Component):
    """智能搜索组件 — 模拟人类的目标发现过程"""

    # 搜索目标
    target_component: Optional[Type[Component]] = None
    max_distance: float = float("inf")
    result_entity: Optional[int] = None

    # 搜索策略
    strategy: str = "visual"
    strategy_history: list = field(default_factory=list)

    # 搜索历史
    search_history: list = field(default_factory=list)
    max_history_size: int = 20

    # 搜索期望
    estimated_probability: float = 0.5
    confidence_threshold: float = 0.3

    # 搜索统计
    last_search_tick: int = 0
    total_searches: int = 0
    successful_searches: int = 0

    # 发现记录
    discoveries: list = field(default_factory=list)

    def to_dict(self) -> dict:
        target = None
        if self.target_component is not None:
            target = f"{self.target_component.__module__}.{self.target_component.__name__}"
        return {
            "target_component": target,
            "max_distance": self.max_distance,
            "result_entity": self.result_entity,
            "strategy": self.strategy,
            "strategy_history": self.strategy_history,
            "search_history": self.search_history,
            "max_history_size": self.max_history_size,
            "estimated_probability": self.estimated_probability,
            "confidence_threshold": self.confidence_threshold,
            "last_search_tick": self.last_search_tick,
            "total_searches": self.total_searches,
            "successful_searches": self.successful_searches,
            "discoveries": self.discoveries,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SearchComponent":
        target_name = data.get("target_component")
        target = None
        if target_name:
            target = ComponentSerializer._registry.get(target_name)
            if target is None:
                try:
                    module_path, class_name = target_name.rsplit(".", 1)
                    module = importlib.import_module(module_path)
                    target = getattr(module, class_name, None)
                except Exception:
                    target = None
        return cls(
            target_component=target,
            max_distance=data.get("max_distance", float("inf")),
            result_entity=data.get("result_entity"),
            strategy=data.get("strategy", "visual"),
            strategy_history=data.get("strategy_history", []),
            search_history=data.get("search_history", []),
            max_history_size=data.get("max_history_size", 20),
            estimated_probability=data.get("estimated_probability", 0.5),
            confidence_threshold=data.get("confidence_threshold", 0.3),
            last_search_tick=data.get("last_search_tick", 0),
            total_searches=data.get("total_searches", 0),
            successful_searches=data.get("successful_searches", 0),
            discoveries=data.get("discoveries", []),
        )