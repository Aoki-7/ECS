#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:conflict_component.py
@说明:冲突状态组件
@时间:2026/05/29
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import List, Dict

from core.component import Component


@dataclass
class ConflictComponent(Component):
    """
    冲突状态组件
    存储实体当前参与的冲突列表
    """
    active_conflicts: List[Dict] = field(default_factory=list)
    # 每项: {
    #   "conflict_id": str,
    #   "type": str,
    #   "opponent_id": int,
    #   "intensity": float,
    #   "strategy": str,
    # }

    def add_conflict(self, conflict: Dict):
        self.active_conflicts.append(conflict)

    def remove_conflict(self, conflict_id: str):
        self.active_conflicts = [
            c for c in self.active_conflicts
            if c.get("conflict_id") != conflict_id
        ]
