#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:brain_component.py
@说明:AI智能组件
@时间:2026/03/13 11:17:50
@作者:Sherry
@版本:1.0
'''


from dataclasses import dataclass, field

from core.component import Component

@dataclass
class BrainComponent(Component):
    """
        AI智能组件
            GOAL
            BehaviorTree
            UtilityAI
            LLM-Agent
    """
    goal: str = None
    memory: list = field(default_factory=list)
    state: str = None