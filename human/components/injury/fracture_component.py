#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:fracture_component.py
@说明:骨折，不一定出血，但影响行动能力
@时间:2026/03/19 13:04:13
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass
from core.component import Component


@dataclass
class FractureComponent(Component):
    """
    骨折：影响移动能力（不直接掉血）
    """
    severity: float = 1.0  # 影响强度（0~1）