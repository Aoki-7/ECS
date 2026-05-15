#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:memory_component.py
@说明:记忆组件
@时间:2026/03/13 22:32:43
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass, field

from core.component import Component

@dataclass
class MemoryComponent(Component):
    events: list = field(default_factory=list)       # 事件记忆
    places: dict = field(default_factory=dict)       # 地点记忆
    people: dict = field(default_factory=dict)       # 人物记忆
