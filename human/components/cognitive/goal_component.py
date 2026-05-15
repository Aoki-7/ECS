#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:goal_component.py
@说明:
@时间:2026/03/13 22:46:59
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass, field

from core.component import Component


@dataclass
class GoalComponent(Component):
    """
        人物长期行为
            - 找食物
            - 赚钱
            - 建立家庭
            - 成为村长
    """
    current_goal: str = None
    long_term_goals: str = None
    priority: int = 0


