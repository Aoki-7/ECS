

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:plate_component.py
@说明:地形板块组件
@时间:2026/03/12 18:11:15
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component



@dataclass
class PlateComponent(Component):
    plate_id: int
    vx: float
    vy: float