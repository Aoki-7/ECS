#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:relationship_component.py
@说明:关系组件
@时间:2026/04/14
@作者:GitHub Copilot
@版本:1.0
'''

from enum import Enum
from dataclasses import dataclass
from typing import Optional

from core.component import Component


class RelationshipStatus(Enum):
    """
    关系状态枚举
    """
    SINGLE = "single"
    DATING = "dating"
    MARRIED = "married"
    DIVORCED = "divorced"


@dataclass
class RelationshipComponent(Component):
    """
    关系组件
    跟踪伴侣和婚姻状态。
    """
    status: RelationshipStatus = RelationshipStatus.SINGLE
    partner_id: Optional[int] = None  # 伴侣实体ID

    # 关系强度 (0-100)
    relationship_strength: float = 0.0