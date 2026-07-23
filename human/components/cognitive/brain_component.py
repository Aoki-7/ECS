#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:brain_component.py
@说明:大脑组件 v2.0 - 纯数据版
'''

from core.component import Component
from dataclasses import dataclass

@dataclass(slots=True)
class BrainComponent(Component):
    """
    大脑组件 - 纯数据版
    存储思维状态和心理健康。
    """
    # 思维状态
    thought: str = ""
    mental_state: str = "stable"

    # 认知能力
    memory_capacity: float = 1.0
    learning_rate: float = 0.5
    attention_span: float = 0.5
    creativity: float = 0.5
    logic_ability: float = 0.5
    intuition: float = 0.5

    # 心理状态
    anxiety: float = 0.0
    depression: float = 0.0
    paranoia: float = 0.0
    confidence: float = 0.5
    curiosity: float = 0.5
    motivation: float = 0.5

    # 意识状态
    consciousness_level: float = 1.0
    is_conscious: bool = True
    is_sleeping: bool = False
    is_dreaming: bool = False

    # 思维记录
    last_thought: str = ""
    thought_count: int = 0