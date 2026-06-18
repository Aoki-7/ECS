#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:inventory_component.py
@说明:库存组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component

@dataclass(slots=True)
class InventoryComponent(Component):
    """
    库存组件 - 纯数据版
    存储物品库存。
    """
    # 物品 {item_id: quantity}
    items: Dict[int, float] = field(default_factory=dict)
    
    # 容量限制
    max_capacity: float = 100.0
    current_weight: float = 0.0
    
    # 装备槽位
    equipped_items: Dict[str, int] = field(default_factory=dict)
    
    # 货币
    currency: float = 0.0
    
    # 交易记录
    trade_history: List[Dict] = field(default_factory=list)
