#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:velocity_component.py
@说明:空间移动速度
@时间:2026/03/14 18:16:27
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

# 已从 human/components/abilities/velocity_component.py 迁移至此
# 向后兼容导入: from human.components.abilities.velocity_component import VelocityComponent
from core.component import Component

@dataclass(slots=True)
class VelocityComponent(Component):
    """
        空间移动速度
    """
    speed: float = 0.0 # 单位 m/s
    vx: float = 0.0
    vy: float = 0.0



