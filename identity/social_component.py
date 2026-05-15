#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:social_component.py
@说明:社会属性
@时间:2026/03/19 13:22:31
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass
from core.component import Component


@dataclass
class SocialComponent(Component):
    """
    社会属性

    Args:
        faction: 阵营 / 组织归属
    """
    faction: str = "neutral"