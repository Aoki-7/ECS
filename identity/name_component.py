#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:name_component.py
@说明:标识组件
@时间:2026/03/19 13:20:15
@作者:Sherry
@版本:1.0
'''

from core.component import Component

from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class NameComponent(Component):
    """
    通用名称组件（适用于所有 Entity）

    Attributes:
        name: 名称（默认展示名称）
        category: 类型（human / animal / item / plant / org / food等）
        description: 描述信息（可选）
        locale_names: 多语言名称映射，例如 {"en": "Human", "zh": "人类"}
    """

    name: str
    category: str = "unknown"

    description: Optional[str] = None
    locale_names: Dict[str, str] = field(default_factory=dict)