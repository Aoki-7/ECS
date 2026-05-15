

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:economy_component.py
@说明:
@时间:2026/03/14 10:54:31
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass
class EconomyComponent(Component):
    """
        经济组件，包含财富、收入和支出等属性
        影响：
            - 消费行为
            - 职业选择
            - 社交关系
        例如：
            wealth高 -> 更倾向于奢侈消费和高端社交
    """
    wealth: float = 0.0
    income: float = 0.0
    expenses: float = 0.0
    
