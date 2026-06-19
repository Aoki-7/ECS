

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:space_component.py
@说明:
@时间:2026/03/09 12:56:41
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass(slots=True)
class SpaceComponent(Component):
    """
    x, y -> 坐标
    layer -> 空间层
        0 地面
        1 空中
        2 地下
        或
        0 实体层
        1 建筑层
        2 逻辑层
    """
    x: int
    y: int

    layer: int = 0
    # 用于检测位置是否变化
    dirty: bool = True