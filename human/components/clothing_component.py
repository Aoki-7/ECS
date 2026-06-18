#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:clothing_component.py
@说明:服装组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component

@dataclass(slots=True)
class ClothingComponent(Component):
    """
    服装组件 - 纯数据版
    存储服装和装备信息。
    """
    # 穿着的服装 {slot: item_id}
    worn_items: Dict[str, int] = field(default_factory=dict)
    
    # 服装状态
    clothing_condition: Dict[int, float] = field(default_factory=dict)
    
    # 保暖值
    insulation: float = 0.0
    
    # 耐久度
    durability: float = 1.0
    
    # 湿度（被雨淋湿等）
    wetness: float = 0.0
    
    # 外观
    appearance_style: str = "basic"
    color_scheme: str = "neutral"


@dataclass(slots=True)
class OutfitComponent(Component):
    """
     outfit组件 - 纯数据版
    存储 outfit 信息。
    """
    # outfit 物品
    outfit_items: List[int] = field(default_factory=list)
    
    # 穿着的服装 {slot: item_id}
    worn_items: Dict[str, int] = field(default_factory=dict)
    
    # outfit 风格
    style: str = "casual"
    
    # 整体保暖值
    total_insulation: float = 0.0
    
    # 整体耐久度
    total_durability: float = 1.0
