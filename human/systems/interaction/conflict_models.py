#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
冲突模型共享模块

集中定义 ConflictType、ResolutionStrategy、RelationshipQuality 和 ConflictInstance，
供 conflict_management_system 与 conflict_resolution_system 共用，避免重复类名。
"""

from dataclasses import dataclass, field
from typing import ClassVar, List, Optional
from enum import Enum, auto


class ConflictType(Enum):
    """冲突类型"""
    RESOURCE = auto()          # 资源争夺
    VALUES = auto()            # 价值观冲突
    RELATIONAL = auto()        # 关系问题
    TASK = auto()              # 任务/目标冲突
    MISCOMMUNICATION = auto()  # 沟通误解


class ResolutionStrategy(Enum):
    """冲突解决策略"""
    AVOIDANCE = auto()         # 回避
    COMPROMISE = auto()        # 妥协
    COMPETITION = auto()       # 竞争
    COLLABORATION = auto()     # 协作
    ACCOMMODATION = auto()     # 迁就
    DIALOGUE = auto()          # 对话沟通


class RelationshipQuality(Enum):
    """关系质量状态"""
    STRAINED = "strained"      # 紧张
    DAMAGED = "damaged"        # 受损
    STABLE = "stable"          # 稳定
    IMPROVED = "improved"      # 改善


@dataclass
class ConflictInstance:
    """冲突实例记录"""
    id: str = ""
    conflict_type: Optional[ConflictType] = None
    parties: List[int] = field(default_factory=list)
    description: str = ""
    intensity: float = 0.0              # 冲突强度 0-100
    current_phase: str = "active"       # active, resolution, resolved
    resolution_method: Optional[str] = None
    outcome: str = ""

    _counter: ClassVar[int] = 0
    _instances: ClassVar[List["ConflictInstance"]] = []

    def __post_init__(self):
        if not self.id:
            ConflictInstance._counter += 1
            self.id = f"conflict_{ConflictInstance._counter}"
        ConflictInstance._instances.append(self)

    def add_party(self, entity_id: int) -> None:
        if entity_id not in self.parties:
            self.parties.append(entity_id)

    def get_participant_count(self) -> int:
        return len(self.parties)