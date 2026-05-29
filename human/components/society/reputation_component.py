#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:reputation_component.py
@说明:声誉相关组件（纯数据）
@时间:2026/04/27
@版本:3.0

业务逻辑已迁移至 human/systems/social/reputation_system.py
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component


@dataclass(slots=True)
class ReputationComponent(Component):
    """
    声誉组件 — 纯数据容器

    在社区中的评价系统。
    所有业务逻辑由 ReputationSystem 管理。
    """
    reputation: float = 50.0           # 当前声誉值 (-50~150 原始值)
    social_status: str = "unknown"     # 社会地位标签
    specialties: Dict[str, int] = field(default_factory=dict)   # 专长领域
    known_for: List[str] = field(default_factory=list)          # 知名领域
    rumors: List[Dict] = field(default_factory=list)            # 谣言列表


@dataclass(slots=True)
class FameComponent(Component):
    """
    声望组件 — 纯数据容器

    区域知名度追踪。
    """
    regional_popularity: Dict[str, float] = field(default_factory=dict)
    regional_reach: Dict[str, int] = field(default_factory=lambda: {"village": 0, "town": 0, "kingdom": 0})
    positive_reports: int = 0
    negative_reports: int = 0


@dataclass(slots=True)
class SocialStandingComponent(Component):
    """
    社会地位组件 — 纯数据容器

    等级制度中的位置。
    """
    class_rank: int = 0
    wealth_tier: str = "unknown"
    political_influence: float = 0.0
    family_status: str = "origin"
