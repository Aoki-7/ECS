#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:skill_component.py
@说明:技能系统
@时间:2026/03/13 22:28:22
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass, field

from core.component import Component

@dataclass
class SkillComponent(Component):
    skills: dict = field(default_factory=lambda: {
        "farming": 1,
        "hunting": 1,
        "crafting": 1,
        "combat": 1,
        "social": 1
    })
    exp: dict = field(default_factory=lambda: {
        "farming": 0,
        "combat": 0
    })