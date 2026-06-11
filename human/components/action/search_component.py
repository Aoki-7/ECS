#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
搜索组件 — 智能目标发现与策略管理

v3.9 迁移：从 core/components/ 移回 human/components/action/
保持 core 层纯粹性。
"""

from dataclasses import dataclass, field
from core.component import Component
from typing import Optional, Type


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
