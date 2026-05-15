

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:surface_material_component.py
@说明:地表物质组件
@时间:2026/03/12 17:56:09
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass(slots=True)
class SurfaceMaterialComponent(Component):
    """
        地表物质组件
        影响：
            - 侵蚀速度
            - 地下水
            - 河流形成
    """
    rock_density: float = 0.0       # 岩石密度 (kg/m^3)
    hardness: float = 0.0         # 硬度
    permeability: float = 0.0      # 渗透率
