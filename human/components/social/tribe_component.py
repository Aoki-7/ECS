#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@文件:tribe_component.py
@说明:部落组件 v3.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component


@dataclass(slots=True)
class TribeComponent(Component):
    """
    部落组件 - 纯数据版
    存储部落信息。
    """
    # 部落成员 {entity_id: role}
    members: Dict[int, str] = field(default_factory=dict)

    # 部落领袖
    leader_id: Optional[int] = None

    # 部落领土
    territory_center: Optional[tuple] = None
    territory_radius: float = 0.0

    # 部落属性
    tribe_name: str = ""
    tribe_size: int = 0
    max_size: int = 50

    # 部落状态
    is_active: bool = True
    founded_tick: int = 0

    # 里程碑标记
    milestones: Dict[str, bool] = field(default_factory=dict)
