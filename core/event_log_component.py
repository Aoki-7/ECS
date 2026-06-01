#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:event_log_component.py
@说明:世界事件日志组件（纯数据）
@时间:2026/05/23
@版本:2.0

业务逻辑已迁移至 core/systems/event_log_system.py
'''

from dataclasses import dataclass, field
from typing import List, Dict, Any
from collections import defaultdict

from core.component import Component


@dataclass(slots=True)
class EventLogComponent(Component):
    """
    世界事件日志组件 — 纯数据容器

    挂载到 WorldEntity 上，记录整个模拟过程中的结构化事件。
    所有 CRUD / 索引 / 裁剪逻辑由 EventLogSystem 管理。
    """

    # 事件列表，按时间顺序（元素类型为 EventRecord）
    events: List[Any] = field(default_factory=list)

    # 索引：按类型快速查询
    _index_by_type: Dict[str, List[int]] = field(
        default_factory=lambda: defaultdict(list), repr=False
    )

    # 索引：按实体快速查询
    _index_by_entity: Dict[int, List[int]] = field(
        default_factory=lambda: defaultdict(list), repr=False
    )

    # 统计计数器
    counters: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
