#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建筑组件 - 纯数据版

v3.0.1 新增 — 建筑实体化
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from core.component import Component


@dataclass(slots=True)
class BuildingComponent(Component):
    """
    建筑组件 - 纯数据

    定义建筑的基本属性。
    """
    building_type: str = "hut"  # hut, workshop, storage, farm
    owner_id: int = -1  # 建造者/所有者 ID
    durability: float = 100.0  # 耐久度
    max_durability: float = 100.0
    capacity: int = 0  # 容量（存储建筑用）
    occupants: List[int] = field(default_factory=list)  # 当前 occupants
    is_active: bool = True  # 是否可用


@dataclass(slots=True)
class BuildingInventoryComponent(Component):
    """
    建筑库存组件 - 纯数据

    存储建筑内的物品。
    """
    items: Dict[int, float] = field(default_factory=dict)  # entity_id -> amount
    max_items: int = 20