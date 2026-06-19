#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:personality_component.py
@说明:性格组件
@时间:2026/03/13 22:25:08
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass(slots=True)
class PersonalityComponent(Component):
    """
        性格组件，包含勇敢、贪婪、善良、好奇心和守序等属性
        影响：
            - 行为概率
            - 社交
            - 职业发展
        例如：
            curiosity高 -> 行为更倾向于探索和学习
    """

    bravery: float = 0.5
    greed: float = 0.5
    kindness: float = 0.5
    curiosity: float = 0.5
    discipline: float = 0.5
