#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
事件日志组件

v3.9 迁移：从 core/ 移回 identity/，保持 core 层纯粹性。
"""

from dataclasses import dataclass, field
from typing import List, Dict
from collections import defaultdict

from core.component import Component


@dataclass(slots=True)
class EventLogComponent(Component):
    """事件日志组件 — 挂载到世界实体上"""

    events: list = field(default_factory=list)
    _index_by_type: Dict[str, list] = field(default_factory=lambda: defaultdict(list))
    _index_by_entity: Dict[int, list] = field(default_factory=lambda: defaultdict(list))
    counters: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
