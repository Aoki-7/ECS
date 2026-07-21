#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矿石类型组件：标识矿石类型，关联特定属性配置
"""
from dataclasses import dataclass
from core.component import Component

@dataclass(slots=True)
class OreTypeComponent(Component):
    """矿石类型组件，仅存储矿石类型标识，具体属性从注册表获取"""
    ore_type_id: str = "stone_ore"  # 矿石类型ID，对应OreRegistry中的配置
