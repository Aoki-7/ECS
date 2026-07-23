#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:dialogue_component.py
@说明:对话状态组件
@时间:2026/05/29
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import List, Optional

from core.component import Component


@dataclass(slots=True)
class DialogueComponent(Component):
    """
    对话状态组件
    存储实体当前的对话上下文
    """
    is_talking: bool = False
    target_entity_id: Optional[int] = None
    topic: str = ""
    sentiment: float = 0.0          # -1 负面, 0 中性, +1 正面
    turn_count: int = 0
    history: List[str] = field(default_factory=list)