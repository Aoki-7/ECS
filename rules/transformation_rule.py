#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:transformation_rule.py
@说明:状态转换规则
@时间:2026/03/25 14:42:32
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass
from typing import Type, Callable

from core.entity import Entity
from core.component import Component

@dataclass
class TransformationRule:
    """
    状态转换规则
    Component（数据）
        ↓
    Rule（转化规则）
        ↓
    System（执行规则）
    """

    # 作用目标组件（必须存在）
    source_component: Type[Component]

    # 条件判断函数
    condition: Callable[[Component], bool]

    # 转化逻辑（对 entity + world 操作）
    transform: Callable[['Entity', 'World'], None]